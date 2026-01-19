"""Google Trends scraper for trending topics - no authentication required."""
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models import Source
from platforms.base import PlatformScraper
from loguru import logger
import requests
from bs4 import BeautifulSoup
import re


class GoogleTrendsScraper(PlatformScraper):
    """Scraper for Google Trends - pulls trending topics without authentication."""
    
    def __init__(self):
        super().__init__("GoogleTrends")
        self.base_url = "https://trends.google.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_posts(self, source: Source, limit: int = 50) -> List[Dict]:
        """
        Fetch trending topics from Google Trends.
        
        Args:
            source: Source object (account_handle can be country code like "KE" for Kenya, "US" for global)
            limit: Maximum number of topics to fetch
        
        Returns:
            List of normalized topic dictionaries
        """
        country = source.account_handle or "US"  # Default to US (global)
        
        try:
            logger.info(f"Fetching Google Trends for country: {country}")
            
            # Fetch trending searches
            # Note: Google Trends API requires special handling
            # We'll use RSS feed or web scraping approach
            trends = self._fetch_trending_topics(country, limit)
            
            posts = []
            for trend_data in trends:
                try:
                    normalized = self.normalize_post(trend_data, source)
                    posts.append(normalized)
                except Exception as e:
                    logger.error(f"Error normalizing trend: {e}")
                    continue
            
            logger.info(f"Fetched {len(posts)} trending topics from Google Trends")
            return posts
            
        except Exception as e:
            self.handle_error(e, source)
            return []
    
    def _fetch_trending_topics(self, country: str, limit: int) -> List[Dict]:
        """
        Fetch trending topics from Google Trends.
        
        Uses pytrends library with proper country code mapping.
        """
        try:
            # Try using pytrends library if available
            try:
                from pytrends.request import TrendReq
                
                # Map country codes for pytrends
                # pytrends uses different country codes than Google Trends RSS
                country_map = {
                    'US': 'united_states',
                    'KE': 'kenya',
                    'ZA': 'south_africa',
                    'GB': 'united_kingdom',
                    'NG': 'nigeria',
                    'GH': 'ghana',
                    'TZ': 'tanzania',
                    'UG': 'uganda'
                }
                pn_code = country_map.get(country.upper(), country.lower())
                
                # Initialize pytrends
                pytrends = TrendReq(hl='en-US', tz=360)
                
                try:
                    # Get daily trending searches
                    # Note: pytrends.trending_searches() may not work for all countries
                    # We'll try it first, then fall back to web scraping
                    trending_df = pytrends.trending_searches(pn=pn_code)
                    
                    if trending_df is not None and not trending_df.empty:
                        trends = []
                        for idx, topic in enumerate(trending_df.head(limit)[0].tolist()):
                            try:
                                topic_str = str(topic).strip()
                                if topic_str:
                                    trend_data = {
                                        'title': topic_str,
                                        'description': f"Trending search in {country}",
                                        'link': f"https://trends.google.com/trends/explore?geo={country}&q={topic_str.replace(' ', '+')}",
                                        'published': datetime.utcnow().isoformat(),
                                        'traffic': '1000+',  # Estimate
                                        'news_items': []
                                    }
                                    trends.append(trend_data)
                            except Exception as e:
                                logger.error(f"Error processing trend topic: {e}")
                                continue
                        
                        if trends:
                            logger.info(f"Successfully fetched {len(trends)} trends using pytrends")
                            return trends
                    
                    # If pytrends returned empty, try web scraping
                    logger.warning(f"pytrends returned empty results for {country}, trying web scraping")
                    return self._scrape_trending_topics(country, limit)
                    
                except Exception as e:
                    logger.warning(f"pytrends trending_searches failed: {e}, trying web scraping")
                    return self._scrape_trending_topics(country, limit)
                    
            except ImportError:
                logger.warning("pytrends not installed, trying web scraping approach")
                return self._scrape_trending_topics(country, limit)
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            return self._scrape_trending_topics(country, limit)
    
    def _scrape_trending_topics(self, country: str, limit: int) -> List[Dict]:
        """
        Scrape trending topics from Google Trends website.
        Uses Playwright to render JavaScript-loaded content.
        """
        try:
            # Correct Google Trends URL format (based on actual working page)
            url = f"https://trends.google.com/trending?geo={country}"
            
            logger.info(f"Scraping Google Trends from: {url}")
            
            # Use Playwright to render JavaScript content
            try:
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    
                    # Wait for trends to load
                    page.wait_for_timeout(3000)  # Give time for content to render
                    
                    # Extract trend topics from the page
                    # Google Trends displays trends in a table - we need to find the actual topic cells
                    trends = []
                    found_topics = set()
                    
                    # Skip these UI texts completely
                    skip_texts = {
                        'trending now', 'explore', 'sign in', 'home', 'search volume',
                        'started', 'past 24', 'trends', 'updated', 'all categories',
                        'all trends', 'by relevance', 'export', country.lower(),
                        'past 24 hours', 'trend breakdown', 'learn more', 'got it',
                        'send feedback', 'about', 'privacy', 'terms', 'settings'
                    }
                    
                    # Strategy: Look for table rows and extract the first meaningful text cell
                    # Google Trends table structure: each row has the trend topic in the first column
                    try:
                        # Find all table rows
                        rows = page.query_selector_all('table tbody tr, tr[role="row"]')
                        
                        for row in rows[:limit * 2]:
                            try:
                                # Get all cells in this row
                                cells = row.query_selector_all('td, th')
                                
                                # The trend topic is usually in the first or second cell
                                for cell_idx, cell in enumerate(cells[:3]):  # Check first 3 cells
                                    text = cell.inner_text().strip()
                                    
                                    if not text or len(text) < 3:
                                        continue
                                    
                                    text_lower = text.lower()
                                    
                                    # Skip if it's clearly UI text
                                    if any(skip in text_lower for skip in skip_texts):
                                        continue
                                    
                                    # Skip if it matches UI patterns
                                    if (text_lower in ['trending', 'search', 'explore', 'sign', 'now', 'in'] or
                                        re.match(r'^\d+[kmb]?\+?$', text_lower) or
                                        re.match(r'^\d+%$', text_lower) or
                                        text_lower in ['ke', 'us', 'za', 'gb'] or
                                        'arrow' in text_lower or
                                        'feedback' in text_lower):
                                        continue
                                    
                                    # Valid trend topic criteria:
                                    # - At least 3 characters
                                    # - Not just numbers
                                    # - Doesn't start with UI keywords
                                    # - Reasonable length (3-60 chars)
                                    if (3 <= len(text) <= 60 and
                                        text[0].isalpha() and
                                        not text.isdigit() and
                                        len(text.split()) <= 8):
                                        found_topics.add(text)
                                        break  # Found a topic in this row, move to next row
                            except:
                                continue
                    except Exception as e:
                        logger.debug(f"Error extracting from table rows: {e}")
                    
                    # If we still don't have enough, try looking for links that might be trends
                    if len(found_topics) < limit:
                        try:
                            links = page.query_selector_all('a[href*="/trends/explore"]')
                            for link in links[:limit * 3]:
                                text = link.inner_text().strip()
                                if (text and 3 <= len(text) <= 60 and
                                    text[0].isalpha() and
                                    not any(skip in text.lower() for skip in skip_texts) and
                                    'trending' not in text.lower() and
                                    'search' not in text.lower()):
                                    found_topics.add(text)
                        except:
                            pass
                    
                    browser.close()
                    
                    # Convert to trend data format
                    for topic in list(found_topics)[:limit]:
                        if topic and len(topic.strip()) > 2:
                            trends.append({
                                'title': topic.strip(),
                                'description': f"Trending search in {country}",
                                'link': f"https://trends.google.com/trends/explore?geo={country}&q={topic.strip().replace(' ', '+')}",
                                'published': datetime.utcnow().isoformat(),
                                'traffic': '1000+',
                                'news_items': []
                            })
                    
                    if trends:
                        logger.info(f"Successfully scraped {len(trends)} trends using Playwright for {country}")
                        return trends
                    else:
                        logger.warning(f"Playwright found page but couldn't extract trends for {country}")
                        # Fall back to requests method
                        return self._scrape_trending_topics_fallback(country, limit)
                        
            except ImportError:
                logger.warning("Playwright not available, using fallback method")
                return self._scrape_trending_topics_fallback(country, limit)
            except Exception as e:
                logger.warning(f"Playwright scraping failed: {e}, using fallback")
                return self._scrape_trending_topics_fallback(country, limit)
            
        except Exception as e:
            logger.error(f"Error in _scrape_trending_topics: {e}")
            return []
    
    def _scrape_trending_topics_fallback(self, country: str, limit: int) -> List[Dict]:
        """Fallback method using requests (may not work if content is JS-loaded)."""
        try:
            url = f"https://trends.google.com/trending?geo={country}"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            trends = []
            
            # Google Trends uses a table-like structure with trend entries
            # Look for trend items - they typically have specific classes or data attributes
            # Try multiple selectors to find trend topics
            
            # Method 1: Look for trend items in the main content area
            trend_containers = soup.find_all(['div', 'tr', 'td'], 
                                            attrs={'class': re.compile(r'trend|search|item|row', re.I)})
            
            # Method 2: Look for links that might be trend topics
            trend_links = soup.find_all('a', href=re.compile(r'/trends/explore|/trending', re.I))
            
            # Method 3: Look for text that might be trend titles (common patterns)
            all_text_elements = soup.find_all(['span', 'div', 'td'], 
                                             string=re.compile(r'[A-Za-z].{3,}', re.I))
            
            # Combine and deduplicate
            found_topics = set()
            
            # Extract from trend containers
            for container in trend_containers[:limit * 3]:  # Check more to find valid ones
                text = container.get_text(strip=True)
                if text and 5 <= len(text) <= 100:  # Reasonable length for a trend topic
                    # Filter out common UI text
                    if not any(skip in text.lower() for skip in ['search volume', 'started', 'past 24', 'trends', 'updated', 'kenya', 'all categories']):
                        found_topics.add(text)
            
            # Extract from trend links
            for link in trend_links[:limit * 2]:
                text = link.get_text(strip=True)
                if text and 5 <= len(text) <= 100:
                    found_topics.add(text)
            
            # Convert to trend data format
            for idx, topic in enumerate(list(found_topics)[:limit]):
                try:
                    # Clean topic name
                    topic_clean = topic.strip()
                    if not topic_clean:
                        continue
                    
                    trend_data = {
                        'title': topic_clean,
                        'description': f"Trending search in {country}",
                        'link': f"https://trends.google.com/trends/explore?geo={country}&q={topic_clean.replace(' ', '+')}",
                        'published': datetime.utcnow().isoformat(),
                        'traffic': '1000+',  # Estimate - actual volume would need more parsing
                        'news_items': []
                    }
                    trends.append(trend_data)
                except Exception as e:
                    logger.debug(f"Error processing topic '{topic}': {e}")
                    continue
            
            if trends:
                logger.info(f"Successfully scraped {len(trends)} trends from Google Trends for {country}")
            else:
                logger.warning(f"Could not extract trending topics from Google Trends page for {country}")
                logger.debug(f"Page title: {soup.title.string if soup.title else 'N/A'}")
            
            return trends[:limit]
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error scraping Google Trends: {e.response.status_code} - {e.response.reason}")
            return []
        except Exception as e:
            logger.error(f"Error scraping Google Trends: {e}")
            return []
    
    def normalize_post(self, raw_data: Dict, source: Source) -> Dict:
        """
        Normalize Google Trends topic to standard format.
        
        Args:
            raw_data: Trend data dictionary
            source: Source object
        
        Returns:
            Normalized post dictionary
        """
        try:
            title = raw_data.get('title', 'Trending Topic')
            
            # Clean the title - remove UI artifacts, icons, numbers, etc.
            # Strategy: Extract meaningful words, skip UI elements and metadata
            
            # Phrases to completely reject
            reject_phrases = [
                'trending now', 'trending up', 'trending down',
                'search explore', 'explore search',
                'sign in', 'sign up', 'sign out',
                'send feedback', 'feedback about',
                'next page', 'previous page',
                'the quality', 'quality of', 'enhance the'
            ]
            
            # First check if the entire title matches a reject phrase
            title_lower = title.lower()
            for phrase in reject_phrases:
                if phrase in title_lower:
                    # This is a UI phrase, try to extract what comes before/after
                    # But if it's the whole thing, reject it
                    if title_lower.strip() == phrase or len(title_lower) - len(phrase) < 3:
                        title_clean = ""
                        break
            
            # Split into words and filter
            words = title.split()
            meaningful_words = []
            
            # Patterns to skip
            skip_patterns = [
                r'^arrow_(upward|downward)$',
                r'^trending_(up|down)$',
                r'^trending$',
                r'^search$',
                r'^explore$',
                r'^sign$',
                r'^\d+%$',  # Percentages
                r'^\d+[KMB]?\+?$',  # Numbers like "2K+", "50K+", "100+"
                r'^in$',
                r'^now$',
                r'^[A-Z]{2}$',  # Country codes like "KE", "US", "ZA"
            ]
            
            skip_words_lower = {
                'trending', 'search', 'in', 'the', 'quality', 'enhance', 
                'arrow_upward', 'arrow_downward', 'send', 'feedback', 'about',
                'next', 'page', 'previous', 'page', 'its', 'this', 'that',
                'more', 'less', 'show', 'hide', 'all', 'none', 'explore',
                'sign', 'now', 'then', 'here', 'there', 'where', 'when'
            }
            
            for word in words:
                word_lower = word.lower()
                # Skip if it matches any skip pattern
                should_skip = False
                for pattern in skip_patterns:
                    if re.match(pattern, word, re.I):
                        should_skip = True
                        break
                
                # Also skip common UI words
                if word_lower in skip_words_lower:
                    should_skip = True
                
                # Skip if it's just a number
                if word.isdigit():
                    should_skip = True
                
                # Skip "Trending search in XX" phrase
                if re.match(r'^Trending\s+search\s+in\s+[A-Z]{2}$', ' '.join(words), re.I):
                    # This is the whole phrase, skip it
                    continue
                
                # Additional checks: skip very short words, single letters, common UI words
                if (not should_skip and 
                    len(word) > 2 and  # At least 3 characters
                    word.isalpha() and  # Only letters (no numbers/symbols)
                    word.lower() not in skip_words_lower):
                    meaningful_words.append(word)
            
            # Join meaningful words
            title_clean = ' '.join(meaningful_words).strip()
            
            # If we got nothing or only numbers/artifacts, try a different approach
            if not title_clean or len(title_clean) < 2 or re.match(r'^[\d%\s]+$', title_clean):
                # Try to find the longest meaningful phrase
                # Remove known patterns and see what's left
                temp = title
                temp = re.sub(r'\b(arrow_upward|arrow_downward|trending_up|trending_down)\b', '', temp, flags=re.I)
                temp = re.sub(r'\b\d+%\b', '', temp)
                temp = re.sub(r'\b\d+[KMB]?\+\b', '', temp)
                temp = re.sub(r'\b\d+\b', '', temp)  # Remove standalone numbers
                temp = re.sub(r'\bTrending search in [A-Z]{2}\b', '', temp, flags=re.I)
                temp = ' '.join(temp.split()).strip()
                
                if temp and len(temp) > 2 and not re.match(r'^[\d%\s]+$', temp):
                    title_clean = temp
                else:
                    # Last resort: use first few words that look like a topic
                    words = title.split()
                    for word in words:
                        word_clean = re.sub(r'[^\w]', '', word)
                        if (len(word_clean) > 2 and 
                            not word_clean.isdigit() and 
                            not re.match(r'^\d+[kmb]?\+?$', word_clean.lower()) and
                            word_clean.lower() not in skip_words_lower and
                            word_clean.upper() not in ['KE', 'US', 'ZA', 'GB', 'NG']):  # Skip country codes
                            title_clean = word_clean
                            break
                    
                    # If still nothing, try to preserve multi-word phrases like "vs eyupspor"
                    if not title_clean or len(title_clean) < 2:
                        # Look for patterns like "word1 word2" where both are meaningful
                        for i in range(len(words) - 1):
                            w1 = re.sub(r'[^\w]', '', words[i])
                            w2 = re.sub(r'[^\w]', '', words[i+1])
                            if (len(w1) > 1 and len(w2) > 2 and
                                w1.lower() not in skip_words_lower and
                                w2.lower() not in skip_words_lower and
                                not w1.isdigit() and not w2.isdigit()):
                                title_clean = f"{w1} {w2}"
                                break
            
            # Final cleanup - remove any remaining artifacts
            title_clean = re.sub(r'\s+', ' ', title_clean).strip()
            
            # Final validation - reject if it looks like UI text
            if title_clean:
                # Reject if it's mostly common words or UI elements
                words_in_title = title_clean.lower().split()
                ui_word_count = sum(1 for w in words_in_title if w in skip_words_lower)
                if len(words_in_title) > 0 and ui_word_count / len(words_in_title) > 0.5:
                    # More than 50% UI words, reject
                    title_clean = ""
                
                # Reject if it's just numbers/percentages
                if re.match(r'^[\d,\.%\s]+$', title_clean):
                    title_clean = ""
                
                # Reject if it's too short or just common words
                if len(title_clean) < 3:
                    title_clean = ""
            
            # If still empty or too short, use a default
            if not title_clean or len(title_clean) < 3:
                title_clean = "Trending Topic"
            
            description = raw_data.get('description', '')
            link = raw_data.get('link', '')
            
            # Extract traffic estimate
            traffic_str = raw_data.get('traffic', '0')
            # Try to extract number from traffic string (e.g., "2K+" -> 2000, "50K+" -> 50000)
            traffic_match = re.search(r'(\d+)([KMB]?)', str(traffic_str).upper())
            if traffic_match:
                num = int(traffic_match.group(1))
                multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(traffic_match.group(2), 1)
                traffic = num * multiplier
            else:
                traffic = int(re.sub(r'[^\d]', '', str(traffic_str))) if traffic_str else 1000
            
            # Get news items count
            news_items = raw_data.get('news_items', [])
            if isinstance(news_items, dict):
                news_items = [news_items]
            news_count = len(news_items) if isinstance(news_items, list) else 0
            
            # Published date
            published_str = raw_data.get('published', '')
            try:
                from dateutil import parser
                posted_at = parser.parse(published_str) if published_str else datetime.utcnow()
            except:
                posted_at = datetime.utcnow()
            
            # Detect Kenyan/African content
            content_lower = (title_clean + " " + description).lower()
            is_kenyan = source.is_kenyan if source else False
            location = source.location if source else None
            
            if not is_kenyan:
                kenyan_keywords = ['kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila']
                if any(kw in content_lower for kw in kenyan_keywords):
                    is_kenyan = True
                    location = "Kenya"
            
            # Estimate engagement based on traffic
            # Google Trends traffic is search volume, we convert to engagement
            # Use traffic to estimate engagement metrics
            base_engagement = max(traffic // 10, 50)  # More realistic base
            likes = max(traffic // 50, base_engagement)
            comments = max(traffic // 200, 10)
            shares = max(traffic // 500, 5)
            views = max(traffic * 5, 1000)  # Estimate views from search volume
            
            # Create normalized data with CLEAN title
            normalized = {
                'platform_post_id': link.split('/')[-1] or str(hash(title_clean)),
                'platform': 'GoogleTrends',
                'author': 'Google Trends',
                'content': title_clean,  # Use clean title as content, not description
                'url': link or f"https://trends.google.com/trending/searches/daily?geo={source.account_handle or 'US'}",
                'posted_at': posted_at,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'views': views,
                'is_kenyan': is_kenyan,
                'location': location,
                'raw_data': json.dumps({
                    'title': title_clean,  # Store clean title
                    'original_title': title,  # Keep original for debugging
                    'description': description,
                    'traffic': traffic_str,
                    'traffic_numeric': traffic,
                    'news_count': news_count,
                    'link': link
                })
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing Google Trends topic: {e}")
            return {
                'platform_post_id': str(hash(str(raw_data))),
                'platform': 'GoogleTrends',
                'author': 'Google Trends',
                'content': raw_data.get('title', 'Trending Topic'),
                'url': raw_data.get('link', 'https://trends.google.com'),
                'posted_at': datetime.utcnow(),
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'views': 0,
                'is_kenyan': False,
                'location': None,
                'raw_data': json.dumps({})
            }
    
    def handle_error(self, error: Exception, source: Source) -> None:
        """Handle errors during Google Trends scraping."""
        logger.error(f"Error fetching Google Trends for {source.account_handle}: {error}")
