"""Facebook platform scraper."""
import json
import requests
from typing import List, Dict
from datetime import datetime
from models import Source
from platforms.base import PlatformScraper
from config import settings
from loguru import logger


class FacebookScraper(PlatformScraper):
    """Scraper for Facebook platform."""
    
    def __init__(self):
        super().__init__("Facebook")
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def fetch_posts(self, source: Source, limit: int = 50) -> List[Dict]:
        """
        Fetch posts from Facebook Page ONLY (not user profiles).
        
        Facebook Pages have public posts that users can see.
        User profiles are ignored as they don't expose trending content.
        """
        if not settings.facebook_access_token:
            logger.warning("Facebook access token not configured")
            return []
        
        try:
            # Get Page ID - MUST be a Page, not a user profile
            page_id = source.account_id
            if not page_id:
                logger.warning(f"Facebook source {source.account_handle} has no account_id (Page ID). "
                             f"Only Facebook Pages are supported, not user profiles.")
                return []
            
            # Only use /posts endpoint for Pages
            url = f"{self.base_url}/{page_id}/posts"
            params = {
                'access_token': settings.facebook_access_token,
                'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares,permalink_url',
                'limit': min(limit, 100)
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', [])
            
            if not posts:
                logger.warning(f"No posts found for Facebook Page {page_id} ({source.account_handle})")
                return []
            
            logger.info(f"Successfully fetched {len(posts)} posts from Facebook Page {source.account_handle}")
            
            normalized_posts = []
            for post in posts:
                normalized = self.normalize_post(post, source)
                normalized_posts.append(normalized)
            
            return normalized_posts
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                error_data = e.response.json() if e.response.content else {}
                error_msg = error_data.get('error', {}).get('message', str(e))
                if 'Unsupported get request' in error_msg or 'Invalid page' in error_msg:
                    logger.warning(f"Facebook source {source.account_handle} (ID: {page_id}) is not a valid Page. "
                                 f"Only Facebook Pages are supported, not user profiles.")
                else:
                    logger.error(f"Facebook API error for {source.account_handle}: {error_msg}")
            elif e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded for Facebook source {source.account_handle}")
                self.handle_rate_limit(e)
            else:
                self.handle_error(e, source)
            return []
        except Exception as e:
            self.handle_error(e, source)
            return []
    
    def normalize_post(self, raw_data: Dict, source: Source) -> Dict:
        """Normalize Facebook post to standard format."""
        likes_data = raw_data.get('likes', {}).get('summary', {})
        comments_data = raw_data.get('comments', {}).get('summary', {})
        shares_data = raw_data.get('shares', {})
        
        return {
            'platform_post_id': raw_data['id'],
            'platform': 'Facebook',
            'author': source.account_name or source.account_handle,
            'content': raw_data.get('message', ''),
            'url': raw_data.get('permalink_url', f"https://facebook.com/{raw_data['id']}"),
            'posted_at': datetime.fromisoformat(raw_data['created_time'].replace('Z', '+00:00')),
            'likes': likes_data.get('total_count', 0),
            'comments': comments_data.get('total_count', 0),
            'shares': shares_data.get('count', 0),
            'views': 0,  # Facebook API doesn't provide views for regular posts
            'raw_data': json.dumps(raw_data)
        }
