"""Twitter/X platform scraper."""
import json
import tweepy
from typing import List, Dict
from datetime import datetime
from models import Source
from platforms.base import PlatformScraper
from config import settings
from loguru import logger


class TwitterScraper(PlatformScraper):
    """Scraper for Twitter/X platform."""
    
    def __init__(self):
        super().__init__("X")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twitter API client."""
        try:
            if settings.twitter_bearer_token:
                self.client = tweepy.Client(
                    bearer_token=settings.twitter_bearer_token,
                    consumer_key=settings.twitter_api_key,
                    consumer_secret=settings.twitter_api_secret,
                    access_token=settings.twitter_access_token,
                    access_token_secret=settings.twitter_access_token_secret,
                    wait_on_rate_limit=True
                )
            else:
                logger.warning("Twitter bearer token not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
    
    def fetch_posts(self, source: Source, limit: int = 50) -> List[Dict]:
        """Fetch tweets from Twitter/X."""
        if not self.client:
            logger.warning("Twitter client not initialized")
            return []
        
        try:
            # Get user ID from handle
            username = source.account_handle.lstrip('@')
            user = self.client.get_user(username=username)
            
            if not user.data:
                logger.warning(f"User {username} not found")
                return []
            
            user_id = user.data.id
            
            # Fetch tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(limit, 100),  # Twitter API max is 100
                tweet_fields=['created_at', 'public_metrics', 'text', 'author_id'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                return []
            
            # Get author info
            authors = {user.id: user for user in tweets.includes.get('users', [])} if tweets.includes else {}
            
            normalized_posts = []
            for tweet in tweets.data:
                author = authors.get(tweet.author_id, user.data) if tweet.author_id else user.data
                normalized = self.normalize_post({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'public_metrics': tweet.public_metrics,
                    'author': author
                }, source)
                normalized_posts.append(normalized)
            
            return normalized_posts
            
        except tweepy.TooManyRequests:
            logger.warning(f"Rate limit exceeded for Twitter source {source.account_handle}")
            self.handle_rate_limit(tweepy.TooManyRequests())
            return []
        except Exception as e:
            self.handle_error(e, source)
            return []
    
    def normalize_post(self, raw_data: Dict, source: Source) -> Dict:
        """Normalize Twitter tweet to standard format."""
        metrics = raw_data.get('public_metrics', {})
        author = raw_data.get('author', {})
        
        return {
            'platform_post_id': str(raw_data['id']),
            'platform': 'X',
            'author': author.get('name', source.account_handle) if isinstance(author, dict) else str(author),
            'content': raw_data.get('text', ''),
            'url': f"https://x.com/{source.account_handle.lstrip('@')}/status/{raw_data['id']}",
            'posted_at': raw_data.get('created_at'),
            'likes': metrics.get('like_count', 0),
            'comments': metrics.get('reply_count', 0),
            'shares': metrics.get('retweet_count', 0),
            'views': metrics.get('impression_count', 0),
            'raw_data': json.dumps(raw_data)
        }
