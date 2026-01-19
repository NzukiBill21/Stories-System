"""RSS feed scraper for trending news - no authentication required."""
import feedparser
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models import Source
from platforms.base import PlatformScraper
from loguru import logger
import re


class RSSScraper(PlatformScraper):
    """Scraper for RSS feeds - pulls trending news without authentication."""
    
    def __init__(self):
        super().__init__("RSS")
    
    def fetch_posts(self, source: Source, limit: int = 50) -> List[Dict]:
        """
        Fetch posts from RSS feed.
        
        Args:
            source: Source object (should have account_handle as RSS URL)
            limit: Maximum number of posts to fetch
        
        Returns:
            List of normalized post dictionaries
        """
        if not source.account_handle or not source.account_handle.startswith('http'):
            logger.warning(f"Invalid RSS URL: {source.account_handle}")
            return []
        
        try:
            logger.info(f"Fetching RSS feed: {source.account_handle}")
            
            # Parse RSS feed
            feed = feedparser.parse(source.account_handle)
            
            if feed.bozo:
                logger.warning(f"RSS feed parsing error: {feed.bozo_exception}")
            
            posts = []
            for entry in feed.entries[:limit]:
                try:
                    normalized = self.normalize_post(entry, source)
                    posts.append(normalized)
                except Exception as e:
                    logger.error(f"Error normalizing RSS entry: {e}")
                    continue
            
            logger.info(f"Fetched {len(posts)} posts from RSS feed")
            return posts
            
        except Exception as e:
            self.handle_error(e, source)
            return []
    
    def normalize_post(self, raw_data, source: Source) -> Dict:
        """
        Normalize RSS entry to standard format.
        
        Args:
            raw_data: FeedParser entry object
            source: Source object
        
        Returns:
            Normalized post dictionary
        """
        try:
            # Extract title
            title = raw_data.get('title', '')
            
            # Extract content/description
            content = ''
            if hasattr(raw_data, 'summary'):
                content = raw_data.summary
            elif hasattr(raw_data, 'description'):
                content = raw_data.description
            elif hasattr(raw_data, 'content'):
                if isinstance(raw_data.content, list) and raw_data.content:
                    content = raw_data.content[0].get('value', '')
            
            # Clean HTML from content
            content = re.sub(r'<[^>]+>', '', content)
            content = content.strip()
            
            # Extract URL
            url = raw_data.get('link', '')
            
            # Extract published date
            published = raw_data.get('published_parsed')
            if published:
                posted_at = datetime(*published[:6])
            else:
                posted_at = datetime.utcnow()
            
            # Extract author
            author = ''
            if hasattr(raw_data, 'author'):
                author = raw_data.author
            elif hasattr(raw_data, 'author_detail'):
                author = raw_data.author_detail.get('name', '')
            
            # For RSS, we simulate engagement based on recency and trending keywords
            # Recent posts get higher "engagement" scores
            # Posts with trending keywords get boosted engagement
            content_lower = (title + " " + content).lower()
            trending_boost = 1.0
            trending_indicators = ['breaking', 'viral', 'trending', 'shocking', 'exclusive', 
                                  'outrage', 'controversy', 'emergency', 'scandal', 'urgent']
            if any(indicator in content_lower for indicator in trending_indicators):
                trending_boost = 3.0  # 3x boost for trending content
            
            hours_old = (datetime.utcnow() - posted_at).total_seconds() / 3600
            if hours_old < 1:
                # Very recent = high engagement
                base_likes = 1000
                base_comments = 100
                base_shares = 50
            elif hours_old < 6:
                base_likes = 500
                base_comments = 50
                base_shares = 25
            else:
                base_likes = 100
                base_comments = 10
                base_shares = 5
            
            # Apply trending boost
            likes = int(base_likes * trending_boost)
            comments = int(base_comments * trending_boost)
            shares = int(base_shares * trending_boost)
            
            # Inherit Kenyan flag and location from source
            is_kenyan = source.is_kenyan if source else False
            location = source.location if source else None
            
            # Also detect Kenyan content from title/content
            content_lower = (title + " " + content).lower()
            if not is_kenyan:
                kenyan_keywords = ['kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila', 'kisumu']
                if any(kw in content_lower for kw in kenyan_keywords):
                    is_kenyan = True
                    if not location:
                        location = "Kenya"
            
            # Create normalized data
            normalized = {
                'platform_post_id': url.split('/')[-1] or str(hash(url)),
                'platform': 'RSS',
                'author': author or source.account_name or 'RSS Feed',
                'content': f"{title}\n\n{content}" if content else title,
                'url': url,
                'posted_at': posted_at,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'views': likes * 10,  # Estimate views
                'is_kenyan': is_kenyan,
                'location': location,
                'raw_data': json.dumps({
                    'title': title,
                    'summary': content,
                    'link': url,
                    'published': raw_data.get('published', ''),
                    'author': author
                })
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing RSS entry: {e}")
            return {
                'platform_post_id': str(hash(str(raw_data))),
                'platform': 'RSS',
                'author': source.account_name or 'RSS Feed',
                'content': str(raw_data.get('title', '')),
                'url': raw_data.get('link', ''),
                'posted_at': datetime.utcnow(),
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'views': 0,
                'raw_data': json.dumps({})
            }
    
    def handle_error(self, error: Exception, source: Source) -> None:
        """Handle errors during RSS scraping."""
        logger.error(f"Error fetching RSS feed {source.account_handle}: {error}")
