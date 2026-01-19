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
        
        Uses RSS feed approach for reliability.
        """
        try:
            # Google Trends RSS feed (daily trending searches)
            rss_url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={country}"
            
            import feedparser
            feed = feedparser.parse(rss_url)
            
            trends = []
            for entry in feed.entries[:limit]:
                try:
                    trend_data = {
                        'title': entry.get('title', ''),
                        'description': entry.get('description', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'traffic': entry.get('ht_approx_traffic', '0'),
                        'news_items': entry.get('ht_news_item', [])
                    }
                    trends.append(trend_data)
                except Exception as e:
                    logger.error(f"Error parsing trend entry: {e}")
                    continue
            
            return trends
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            # Fallback: return empty list
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
            description = raw_data.get('description', '')
            link = raw_data.get('link', '')
            
            # Extract traffic estimate
            traffic_str = raw_data.get('traffic', '0')
            traffic = int(re.sub(r'[^\d]', '', traffic_str)) if traffic_str else 0
            
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
            content_lower = (title + " " + description).lower()
            is_kenyan = source.is_kenyan if source else False
            location = source.location if source else None
            
            if not is_kenyan:
                kenyan_keywords = ['kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila']
                if any(kw in content_lower for kw in kenyan_keywords):
                    is_kenyan = True
                    location = "Kenya"
            
            # Estimate engagement based on traffic
            # Google Trends traffic is search volume, we convert to engagement
            likes = max(traffic // 100, 100)  # Base engagement
            comments = max(traffic // 500, 10)
            shares = max(traffic // 1000, 5)
            views = traffic * 10  # Estimate views from search volume
            
            # Create normalized data
            normalized = {
                'platform_post_id': link.split('/')[-1] or str(hash(title)),
                'platform': 'GoogleTrends',
                'author': 'Google Trends',
                'content': f"{title}\n\n{description}" if description else title,
                'url': link or f"https://trends.google.com/trending/searches/daily?geo={source.account_handle or 'US'}",
                'posted_at': posted_at,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'views': views,
                'is_kenyan': is_kenyan,
                'location': location,
                'raw_data': json.dumps({
                    'title': title,
                    'description': description,
                    'traffic': traffic_str,
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
