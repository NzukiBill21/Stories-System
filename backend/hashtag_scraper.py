"""Hashtag-based scraping service for tracking trending hashtags."""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Dict, Optional
from models import Hashtag, RawPost, Source
from platforms import get_scraper
from platforms.twitter import TwitterScraper
from platforms.facebook import FacebookScraper
from platforms.instagram import InstagramScraper
from platforms.tiktok import TikTokScraper
from kenyan_sources_config import KENYAN_HASHTAGS, get_hashtags_for_platform
from loguru import logger
import json


def scrape_hashtag_twitter(db: Session, hashtag: Hashtag) -> List[Dict]:
    """Scrape Twitter/X posts by hashtag."""
    try:
        scraper = TwitterScraper()
        if not scraper.client:
            logger.warning("Twitter client not initialized")
            return []
        
        # Twitter API v2 search for hashtags
        query = f"#{hashtag.hashtag.lstrip('#')} -is:retweet lang:en"
        
        try:
            # Twitter API v2 search for hashtags
            # Note: Requires Twitter API v2 access with search permissions
            tweets = scraper.client.search_recent_tweets(
                query=query,
                max_results=min(hashtag.posts_per_hashtag, 100),
                tweet_fields=['created_at', 'public_metrics', 'text', 'author_id'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                return []
            
            # Get author info
            authors = {user.id: user for user in tweets.includes.get('users', [])} if tweets.includes else {}
            
            normalized_posts = []
            for tweet in tweets.data:
                author = authors.get(tweet.author_id) if tweet.author_id else None
                author_name = author.name if author else "Unknown"
                
                # Extract location if available
                location = None
                if hasattr(tweet, 'geo') and tweet.geo:
                    location = tweet.geo.get('place_id')
                
                normalized = {
                    'platform_post_id': str(tweet.id),
                    'platform': 'X',
                    'author': author_name,
                    'content': tweet.text,
                    'url': f"https://x.com/i/web/status/{tweet.id}",
                    'posted_at': tweet.created_at,
                    'likes': tweet.public_metrics.get('like_count', 0),
                    'comments': tweet.public_metrics.get('reply_count', 0),
                    'shares': tweet.public_metrics.get('retweet_count', 0),
                    'views': tweet.public_metrics.get('impression_count', 0),
                    'location': location,
                    'is_kenyan': hashtag.is_kenyan,
                    'raw_data': json.dumps(tweet.data if hasattr(tweet, 'data') else str(tweet))
                }
                normalized_posts.append(normalized)
            
            return normalized_posts
            
        except Exception as e:
            logger.error(f"Error searching Twitter for #{hashtag.hashtag}: {e}")
            return []
            
    except Exception as e:
        logger.error(f"Error in Twitter hashtag scraping: {e}")
        return []


def scrape_hashtag_instagram(db: Session, hashtag: Hashtag) -> List[Dict]:
    """Scrape Instagram posts by hashtag."""
    try:
        scraper = InstagramScraper()
        from config import settings
        
        if not settings.instagram_access_token:
            logger.warning("Instagram access token not configured")
            return []
        
        # Instagram Graph API hashtag search
        # Note: Requires Instagram Business Account and special permissions
        hashtag_id = None
        
        try:
            # First, get hashtag ID
            search_url = f"{scraper.base_url}/ig_hashtag_search"
            params = {
                'user_id': settings.instagram_access_token.split('.')[0],  # Extract user ID from token
                'q': hashtag.hashtag.lstrip('#'),
                'access_token': settings.instagram_access_token
            }
            
            # This is a simplified version - Instagram hashtag API requires business account
            # For now, return empty and log warning
            logger.warning(f"Instagram hashtag search requires Business Account setup")
            return []
            
        except Exception as e:
            logger.error(f"Error searching Instagram for #{hashtag.hashtag}: {e}")
            return []
            
    except Exception as e:
        logger.error(f"Error in Instagram hashtag scraping: {e}")
        return []


def scrape_hashtag_facebook(db: Session, hashtag: Hashtag) -> List[Dict]:
    """Scrape Facebook posts by hashtag."""
    try:
        scraper = FacebookScraper()
        from config import settings
        
        if not settings.facebook_access_token:
            logger.warning("Facebook access token not configured")
            return []
        
        # Facebook Graph API doesn't have direct hashtag search
        # We can search posts, but hashtag search is limited
        # For now, return empty and suggest using page-based scraping
        logger.warning(f"Facebook hashtag search is limited - use page-based scraping instead")
        return []
        
    except Exception as e:
        logger.error(f"Error in Facebook hashtag scraping: {e}")
        return []


def scrape_hashtag_tiktok(db: Session, hashtag: Hashtag) -> List[Dict]:
    """Scrape TikTok videos by hashtag."""
    try:
        scraper = TikTokScraper()
        
        # TikTokApi doesn't have direct hashtag search in current version
        # Would need to use trending and filter by hashtag in content
        # For now, return empty
        logger.warning(f"TikTok hashtag search not directly supported - use trending videos")
        return []
        
    except Exception as e:
        logger.error(f"Error in TikTok hashtag scraping: {e}")
        return []


def scrape_hashtag(db: Session, hashtag_id: int) -> dict:
    """
    Scrape posts for a specific hashtag across platforms.
    
    Args:
        db: Database session
        hashtag_id: ID of hashtag to scrape
    
    Returns:
        Dictionary with scraping results
    """
    hashtag = db.query(Hashtag).filter(Hashtag.id == hashtag_id).first()
    if not hashtag:
        return {"error": "Hashtag not found", "posts_fetched": 0}
    
    if not hashtag.is_active:
        return {"error": "Hashtag is not active", "posts_fetched": 0}
    
    scrape_start = datetime.utcnow()
    posts_fetched = 0
    posts_saved = 0
    
    try:
        # Determine which platforms to scrape
        platforms_to_scrape = []
        if hashtag.platform == "all":
            platforms_to_scrape = ["X", "Instagram", "Facebook", "TikTok"]
        else:
            platforms_to_scrape = [hashtag.platform]
        
        all_posts = []
        
        # Scrape each platform
        for platform in platforms_to_scrape:
            try:
                if platform == "X" or platform == "Twitter":
                    posts = scrape_hashtag_twitter(db, hashtag)
                elif platform == "Instagram":
                    posts = scrape_hashtag_instagram(db, hashtag)
                elif platform == "Facebook":
                    posts = scrape_hashtag_facebook(db, hashtag)
                elif platform == "TikTok":
                    posts = scrape_hashtag_tiktok(db, hashtag)
                else:
                    continue
                
                all_posts.extend(posts)
                posts_fetched += len(posts)
                
            except Exception as e:
                logger.error(f"Error scraping {platform} for #{hashtag.hashtag}: {e}")
                continue
        
        # Save posts to database
        for post_data in all_posts:
            try:
                # Check if post already exists
                existing = db.query(RawPost).filter(
                    and_(
                        RawPost.platform == post_data['platform'],
                        RawPost.platform_post_id == post_data['platform_post_id']
                    )
                ).first()
                
                if existing:
                    continue  # Skip duplicates
                
                # Create raw post
                raw_post = RawPost(
                    hashtag_id=hashtag.id,
                    platform_post_id=post_data['platform_post_id'],
                    platform=post_data['platform'],
                    author=post_data['author'],
                    content=post_data.get('content', ''),
                    url=post_data['url'],
                    posted_at=post_data['posted_at'],
                    likes=post_data.get('likes', 0),
                    comments=post_data.get('comments', 0),
                    shares=post_data.get('shares', 0),
                    views=post_data.get('views', 0),
                    location=post_data.get('location'),
                    is_kenyan=post_data.get('is_kenyan', hashtag.is_kenyan),
                    media_url=post_data.get('media_url'),
                    raw_data=post_data.get('raw_data', '')
                )
                
                db.add(raw_post)
                posts_saved += 1
                
            except Exception as e:
                logger.error(f"Error saving post: {e}")
                continue
        
        # Update hashtag last_scraped_at
        hashtag.last_scraped_at = datetime.utcnow()
        db.commit()
        
        scrape_end = datetime.utcnow()
        duration = (scrape_end - scrape_start).total_seconds()
        
        logger.info(f"Hashtag #{hashtag.hashtag}: Fetched {posts_fetched} posts, saved {posts_saved}")
        
        return {
            "success": True,
            "hashtag": hashtag.hashtag,
            "posts_fetched": posts_fetched,
            "posts_saved": posts_saved,
            "duration_seconds": duration
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error scraping hashtag #{hashtag.hashtag}: {e}")
        return {"error": str(e), "posts_fetched": 0}
