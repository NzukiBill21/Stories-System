"""Instagram platform scraper."""
import json
import requests
from typing import List, Dict
from datetime import datetime
from models import Source
from platforms.base import PlatformScraper
from config import settings
from loguru import logger


class InstagramScraper(PlatformScraper):
    """Scraper for Instagram platform."""
    
    def __init__(self):
        super().__init__("Instagram")
        self.base_url = "https://graph.instagram.com/v18.0"
    
    def fetch_posts(self, source: Source, limit: int = 50) -> List[Dict]:
        """Fetch posts from Instagram account."""
        # Try Instagram token first
        instagram_token = settings.instagram_access_token
        
        # Fallback: Try Facebook page token if Instagram token not available
        facebook_token = settings.facebook_access_token
        
        if not instagram_token and not facebook_token:
            logger.warning("Neither Instagram nor Facebook access token configured")
            return []
        
        try:
            # Get account ID from handle or use account_id
            account_id = source.account_id or source.account_handle
            
            # Try Instagram API first
            token_to_use = instagram_token if instagram_token else facebook_token
            
            url = f"{self.base_url}/{account_id}/media"
            params = {
                'access_token': token_to_use,
                'fields': 'id,caption,timestamp,permalink,like_count,comments_count,media_type',
                'limit': min(limit, 100)
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            # If Instagram API fails, try Facebook Graph API for Instagram Business Account
            if response.status_code == 400:
                error_data = response.json()
                if 'error' in error_data:
                    error_code = error_data['error'].get('code')
                    error_message = error_data['error'].get('message', '')
                    
                    # If it's a token/permission error, try Facebook Graph API
                    if error_code in [190, 10, 200] or 'permission' in error_message.lower():
                        logger.info(f"Instagram API failed, trying Facebook Graph API for Instagram Business Account")
                        return self._fetch_via_facebook_api(source, limit, facebook_token)
            
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', [])
            
            normalized_posts = []
            for post in posts:
                normalized = self.normalize_post(post, source)
                normalized_posts.append(normalized)
            
            return normalized_posts
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded for Instagram source {source.account_handle}")
                self.handle_rate_limit(e)
            else:
                # Try Facebook API as fallback
                if facebook_token:
                    logger.info("Trying Facebook Graph API as fallback")
                    return self._fetch_via_facebook_api(source, limit, facebook_token)
                self.handle_error(e, source)
            return []
        except Exception as e:
            # Try Facebook API as fallback
            if facebook_token:
                logger.info("Trying Facebook Graph API as fallback")
                return self._fetch_via_facebook_api(source, limit, facebook_token)
            self.handle_error(e, source)
            return []
    
    def _fetch_via_facebook_api(self, source: Source, limit: int, facebook_token: str) -> List[Dict]:
        """Try fetching Instagram posts via Facebook Graph API (for Business Accounts)."""
        try:
            # First, check if source has a Facebook page ID
            # If account_id looks like a Facebook page ID, use it
            page_id = source.account_id
            
            if not page_id:
                logger.warning("No account ID available for Facebook API fallback")
                return []
            
            # Check if page has Instagram Business Account
            fb_url = f"https://graph.facebook.com/v18.0/{page_id}"
            params = {
                'fields': 'instagram_business_account',
                'access_token': facebook_token
            }
            
            response = requests.get(fb_url, params=params, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Could not get Instagram Business Account for page {page_id}")
                return []
            
            data = response.json()
            ig_business_account = data.get('instagram_business_account')
            
            if not ig_business_account:
                logger.warning(f"Page {page_id} does not have Instagram Business Account connected")
                return []
            
            ig_account_id = ig_business_account.get('id')
            logger.info(f"Found Instagram Business Account: {ig_account_id}")
            
            # Fetch Instagram posts via Facebook Graph API
            ig_url = f"https://graph.facebook.com/v18.0/{ig_account_id}/media"
            params = {
                'fields': 'id,caption,timestamp,permalink,like_count,comments_count,media_type',
                'limit': min(limit, 100),
                'access_token': facebook_token
            }
            
            response = requests.get(ig_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', [])
            
            normalized_posts = []
            for post in posts:
                normalized = self.normalize_post(post, source)
                normalized_posts.append(normalized)
            
            logger.info(f"Fetched {len(normalized_posts)} Instagram posts via Facebook API")
            return normalized_posts
            
        except Exception as e:
            logger.error(f"Error fetching via Facebook API: {e}")
            return []
    
    def normalize_post(self, raw_data: Dict, source: Source) -> Dict:
        """Normalize Instagram post to standard format."""
        return {
            'platform_post_id': raw_data['id'],
            'platform': 'Instagram',
            'author': source.account_name or source.account_handle,
            'content': raw_data.get('caption', ''),
            'url': raw_data.get('permalink', f"https://instagram.com/p/{raw_data['id']}"),
            'posted_at': datetime.fromisoformat(raw_data['timestamp'].replace('Z', '+00:00')),
            'likes': raw_data.get('like_count', 0),
            'comments': raw_data.get('comments_count', 0),
            'shares': 0,  # Instagram doesn't have shares
            'views': 0,  # Views not available in basic API
            'raw_data': json.dumps(raw_data)
        }
