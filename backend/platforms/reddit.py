"""Reddit scraper for trending content - uses public API, no authentication required."""
import json
from typing import List, Dict, Optional
from datetime import datetime
from models import Source
from platforms.base import PlatformScraper
from loguru import logger
import requests


class RedditScraper(PlatformScraper):
    """Scraper for Reddit - pulls trending posts without authentication."""
    
    def __init__(self):
        super().__init__("Reddit")
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': 'StoryIntelligence/1.0 (Media Monitoring Bot)'
        }
    
    def fetch_posts(self, source: Source, limit: int = 50) -> List[Dict]:
        """
        Fetch trending posts from Reddit.
        
        Args:
            source: Source object (account_handle should be subreddit name like "worldnews" or "news")
            limit: Maximum number of posts to fetch
        
        Returns:
            List of normalized post dictionaries
        """
        subreddit = source.account_handle or "popular"
        if not subreddit.startswith('r/') and not subreddit.startswith('/r/'):
            subreddit = f"r/{subreddit}"
        
        # Remove r/ prefix for URL
        subreddit_clean = subreddit.replace('r/', '').replace('/', '')
        
        try:
            # Fetch trending posts from subreddit
            url = f"{self.base_url}/{subreddit}/hot.json"
            params = {'limit': min(limit, 100)}
            
            logger.info(f"Fetching Reddit posts from {subreddit}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            posts = []
            for child in data.get('data', {}).get('children', [])[:limit]:
                try:
                    post_data = child.get('data', {})
                    normalized = self.normalize_post(post_data, source)
                    posts.append(normalized)
                except Exception as e:
                    logger.error(f"Error normalizing Reddit post: {e}")
                    continue
            
            logger.info(f"Fetched {len(posts)} posts from Reddit")
            return posts
            
        except Exception as e:
            self.handle_error(e, source)
            return []
    
    def normalize_post(self, raw_data: Dict, source: Source) -> Dict:
        """
        Normalize Reddit post to standard format.
        
        Args:
            raw_data: Reddit post data dictionary
            source: Source object
        
        Returns:
            Normalized post dictionary
        """
        try:
            # Extract post ID
            post_id = raw_data.get('id', '')
            
            # Extract title
            title = raw_data.get('title', '')
            
            # Extract selftext (post content)
            selftext = raw_data.get('selftext', '')
            
            # Extract URL
            url = raw_data.get('url', '')
            if url.startswith('/'):
                url = f"{self.base_url}{url}"
            
            # Extract author
            author = raw_data.get('author', '[deleted]')
            
            # Extract engagement metrics
            ups = raw_data.get('ups', 0)  # Upvotes
            downs = raw_data.get('downs', 0)  # Downvotes
            num_comments = raw_data.get('num_comments', 0)
            score = raw_data.get('score', 0)
            
            # Extract timestamp
            created_utc = raw_data.get('created_utc', 0)
            if created_utc:
                posted_at = datetime.fromtimestamp(created_utc)
            else:
                posted_at = datetime.utcnow()
            
            # Extract subreddit
            subreddit = raw_data.get('subreddit', '')
            
            # Combine title and content
            content = title
            if selftext:
                content = f"{title}\n\n{selftext}"
            
            # Inherit Kenyan flag and location from source
            is_kenyan = source.is_kenyan if source else False
            location = source.location if source else None
            
            # Detect Kenyan/African content from subreddit or content
            if not is_kenyan:
                kenyan_subreddits = ['kenya', 'nairobi']
                african_subreddits = ['kenya', 'nigeria', 'southafrica', 'ghana', 'tanzania', 'uganda', 'africa']
                
                if subreddit.lower() in kenyan_subreddits:
                    is_kenyan = True
                    location = "Kenya"
                elif subreddit.lower() in african_subreddits:
                    location = subreddit.capitalize() if subreddit != 'southafrica' else 'South Africa'
            
            # Also detect from content
            content_lower = content.lower()
            if not is_kenyan:
                kenyan_keywords = ['kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila']
                if any(kw in content_lower for kw in kenyan_keywords):
                    is_kenyan = True
                    if not location:
                        location = "Kenya"
            
            # Create normalized data
            # Reddit upvotes = likes, comments = comments, shares estimated
            normalized = {
                'platform_post_id': post_id,
                'platform': 'Reddit',
                'author': f"u/{author}",
                'content': content,
                'url': f"{self.base_url}{raw_data.get('permalink', '')}" if raw_data.get('permalink') else url,
                'posted_at': posted_at,
                'likes': ups,  # Upvotes as likes
                'comments': num_comments,
                'shares': max(0, score // 10),  # Estimate shares from score
                'views': score * 5,  # Estimate views
                'is_kenyan': is_kenyan,
                'location': location,
                'raw_data': json.dumps({
                    'subreddit': subreddit,
                    'score': score,
                    'ups': ups,
                    'downs': downs,
                    'num_comments': num_comments,
                    'permalink': raw_data.get('permalink', '')
                })
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing Reddit post: {e}")
            return {
                'platform_post_id': raw_data.get('id', 'unknown'),
                'platform': 'Reddit',
                'author': source.account_name or 'Reddit User',
                'content': raw_data.get('title', ''),
                'url': raw_data.get('url', ''),
                'posted_at': datetime.utcnow(),
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'views': 0,
                'raw_data': json.dumps({})
            }
    
    def handle_error(self, error: Exception, source: Source) -> None:
        """Handle errors during Reddit scraping."""
        logger.error(f"Error fetching Reddit posts from {source.account_handle}: {error}")
