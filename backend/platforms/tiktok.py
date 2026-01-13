"""TikTok platform scraper using TikTokApi."""
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models import Source
from platforms.base import PlatformScraper
from config import settings
from loguru import logger
import time


class TikTokScraper(PlatformScraper):
    """Scraper for TikTok platform using TikTokApi."""
    
    def __init__(self):
        super().__init__("TikTok")
        self.api = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize TikTok API client."""
        try:
            from TikTokApi import TikTokApi
            import asyncio
            
            # TikTokApi requires async initialization
            # We'll use a sync wrapper for compatibility
            self.api_class = TikTokApi
            logger.info("TikTok scraper initialized")
        except ImportError:
            logger.warning("TikTokApi not installed. Install with: pip install TikTokApi playwright")
            logger.warning("Then run: playwright install chromium")
            self.api_class = None
        except Exception as e:
            logger.error(f"Failed to initialize TikTok API: {e}")
            self.api_class = None
    
    def _run_async(self, coro):
        """Run async function synchronously."""
        try:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"Error running async function: {e}")
            return None
    
    def fetch_posts(self, source: Source, limit: int = 50) -> List[Dict]:
        """
        Fetch trending TikTok videos.
        
        Args:
            source: Source object (for TikTok, we fetch trending, not user-specific)
            limit: Maximum number of videos to fetch
        
        Returns:
            List of normalized video dictionaries
        """
        if not self.api_class:
            logger.warning("TikTok API not available")
            return []
        
        try:
            # Use configured limit or provided limit
            fetch_limit = min(limit, settings.tiktok_trending_limit)
            
            logger.info(f"Fetching {fetch_limit} trending TikTok videos...")
            
            # Fetch trending videos
            videos = self._fetch_trending_videos(fetch_limit)
            
            if not videos:
                logger.warning("No videos fetched from TikTok")
                return []
            
            # Normalize and filter videos
            normalized_videos = []
            for video_data in videos:
                try:
                    normalized = self.normalize_post(video_data, source)
                    
                    # Calculate engagement velocity
                    velocity = self._calculate_engagement_velocity(normalized)
                    
                    # Filter: only keep high-engagement videos
                    if velocity >= settings.tiktok_min_engagement_velocity:
                        normalized_videos.append(normalized)
                        logger.debug(f"Video {normalized['platform_post_id']} passed filter (velocity: {velocity:.1f})")
                    else:
                        logger.debug(f"Video {normalized['platform_post_id']} filtered out (velocity: {velocity:.1f} < {settings.tiktok_min_engagement_velocity})")
                        
                except Exception as e:
                    logger.error(f"Error normalizing TikTok video: {e}")
                    continue
            
            logger.info(f"Fetched {len(videos)} videos, {len(normalized_videos)} passed engagement filter")
            return normalized_videos
            
        except Exception as e:
            self.handle_error(e, source)
            return []
    
    def _fetch_trending_videos(self, limit: int) -> List[Dict]:
        """Fetch trending videos from TikTok."""
        try:
            from TikTokApi import TikTokApi
            
            async def get_trending():
                """Async function to get trending videos."""
                async with TikTokApi() as api:
                    # TikTokApi trending() returns a generator
                    # Need to iterate properly
                    videos = []
                    count = 0
                    try:
                        # Try with count parameter first
                        trending = api.trending(count=limit)
                        if hasattr(trending, '__aiter__'):
                            async for video in trending:
                                videos.append(video)
                                count += 1
                                if count >= limit:
                                    break
                        else:
                            # If it's not async iterable, try to get items directly
                            for i in range(limit):
                                try:
                                    video = await trending.__anext__() if hasattr(trending, '__anext__') else next(trending)
                                    videos.append(video)
                                except (StopAsyncIteration, StopIteration):
                                    break
                    except (TypeError, AttributeError):
                        # Fallback: try without count
                        try:
                            trending = api.trending()
                            async for video in trending:
                                videos.append(video)
                                count += 1
                                if count >= limit:
                                    break
                        except Exception as e:
                            logger.error(f"Error iterating TikTok trending: {e}")
                            return []
                    
                    return videos
            
            videos = self._run_async(get_trending())
            
            if videos is None:
                return []
            
            # Convert TikTokApi video objects to dictionaries
            video_dicts = []
            for video in videos:
                try:
                    video_dict = {
                        'id': video.get('id', ''),
                        'desc': video.get('desc', ''),
                        'author': video.get('author', {}),
                        'stats': video.get('stats', {}),
                        'createTime': video.get('createTime', 0),
                        'video': video.get('video', {}),
                        'webVideoUrl': video.get('webVideoUrl', ''),
                        'as_dict': video.as_dict if hasattr(video, 'as_dict') else None
                    }
                    video_dicts.append(video_dict)
                except Exception as e:
                    logger.error(f"Error processing video: {e}")
                    continue
            
            return video_dicts
            
        except Exception as e:
            logger.error(f"Error fetching trending videos: {e}")
            # Fallback: try alternative method
            return self._fetch_trending_fallback(limit)
    
    def _fetch_trending_fallback(self, limit: int) -> List[Dict]:
        """Fallback method if TikTokApi fails."""
        logger.warning("Using fallback method for TikTok scraping")
        # This could use web scraping or alternative API
        # For now, return empty list
        return []
    
    def _calculate_engagement_velocity(self, normalized_video: Dict) -> float:
        """
        Calculate engagement velocity for a video.
        
        Formula: (likes + comments + shares) / minutes_since_posted
        
        Args:
            normalized_video: Normalized video dictionary
        
        Returns:
            Engagement velocity (engagement per minute)
        """
        try:
            posted_at = normalized_video.get('posted_at')
            if not posted_at:
                logger.warning("No posted_at timestamp, cannot calculate velocity")
                return 0.0
            
            # Ensure posted_at is a datetime object
            if isinstance(posted_at, datetime):
                posted_dt = posted_at
            elif isinstance(posted_at, (int, float)):
                # Timestamp in seconds
                posted_dt = datetime.fromtimestamp(posted_at)
            else:
                logger.warning(f"Invalid posted_at format: {type(posted_at)}")
                return 0.0
            
            # Calculate minutes since posted
            current_time = datetime.utcnow()
            time_diff = current_time - posted_dt
            minutes_elapsed = max(time_diff.total_seconds() / 60, 0.1)  # At least 0.1 minutes
            
            # Get engagement metrics
            likes = int(normalized_video.get('likes', 0) or 0)
            comments = int(normalized_video.get('comments', 0) or 0)
            shares = int(normalized_video.get('shares', 0) or 0)
            
            # Calculate velocity: (likes + comments + shares) / minutes_since_posted
            total_engagement = likes + comments + shares
            velocity = total_engagement / minutes_elapsed
            
            logger.debug(f"Velocity calculation: {total_engagement} engagement / {minutes_elapsed:.2f} min = {velocity:.2f}/min")
            
            return velocity
            
        except Exception as e:
            logger.error(f"Error calculating engagement velocity: {e}")
            return 0.0
    
    def normalize_post(self, raw_data: Dict, source: Source) -> Dict:
        """
        Normalize TikTok video to standard format.
        
        Args:
            raw_data: Raw video data from TikTokApi
            source: Source object
        
        Returns:
            Normalized video dictionary
        """
        try:
            # Extract video ID
            video_id = str(raw_data.get('id', ''))
            
            # Extract caption/description
            caption = raw_data.get('desc', '') or raw_data.get('description', '')
            
            # Extract author information
            author_data = raw_data.get('author', {})
            if isinstance(author_data, dict):
                author_username = author_data.get('uniqueId', '') or author_data.get('nickname', '')
                author_name = author_data.get('nickname', '') or author_username
            else:
                author_username = str(author_data) if author_data else ''
                author_name = author_username
            
            # Extract stats
            stats = raw_data.get('stats', {})
            likes = stats.get('diggCount', 0) or stats.get('likes', 0) or 0
            comments = stats.get('commentCount', 0) or stats.get('comments', 0) or 0
            shares = stats.get('shareCount', 0) or stats.get('shares', 0) or 0
            views = stats.get('playCount', 0) or stats.get('views', 0) or stats.get('viewCount', 0) or 0
            
            # Extract timestamp
            create_time = raw_data.get('createTime', 0)
            if create_time:
                # TikTok timestamps are in seconds
                posted_at = datetime.fromtimestamp(create_time)
            else:
                posted_at = datetime.utcnow()
            
            # Extract video URL
            video_url = raw_data.get('webVideoUrl', '')
            if not video_url:
                # Construct URL from video ID
                video_url = f"https://www.tiktok.com/@tiktok/video/{video_id}"
            
            # Extract video download URL (if available)
            video_data = raw_data.get('video', {})
            media_url = video_data.get('downloadAddr', '') or video_data.get('playAddr', '')
            
            # Create normalized data
            normalized = {
                'platform_post_id': video_id,
                'platform': 'TikTok',
                'author': author_name or author_username or 'TikTok User',
                'content': caption,
                'url': video_url,
                'posted_at': posted_at,
                'likes': int(likes) if likes else 0,
                'comments': int(comments) if comments else 0,
                'shares': int(shares) if shares else 0,
                'views': int(views) if views else 0,
                'raw_data': json.dumps(raw_data) if not isinstance(raw_data, str) else raw_data
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing TikTok video data: {e}")
            # Return minimal valid structure
            return {
                'platform_post_id': str(raw_data.get('id', 'unknown')),
                'platform': 'TikTok',
                'author': source.account_name or source.account_handle or 'TikTok User',
                'content': raw_data.get('desc', '') or '',
                'url': raw_data.get('webVideoUrl', 'https://www.tiktok.com'),
                'posted_at': datetime.utcnow(),
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'views': 0,
                'raw_data': json.dumps(raw_data) if not isinstance(raw_data, str) else str(raw_data)
            }
    
    def handle_rate_limit(self, error: Exception) -> None:
        """Handle TikTok rate limiting."""
        logger.warning("TikTok rate limit encountered, waiting...")
        time.sleep(settings.rate_limit_delay * 30)  # Wait longer for TikTok
    
    def handle_error(self, error: Exception, source: Source) -> None:
        """Handle errors during TikTok scraping."""
        logger.error(f"Error fetching TikTok videos for {source.account_handle}: {error}")
        logger.error(f"Error type: {type(error).__name__}")
        
        # Check for specific TikTok API errors
        error_str = str(error).lower()
        if 'rate limit' in error_str or '429' in error_str:
            self.handle_rate_limit(error)
        elif 'not found' in error_str or '404' in error_str:
            logger.warning("TikTok video or user not found")
        elif 'network' in error_str or 'connection' in error_str:
            logger.warning("Network error connecting to TikTok")
        else:
            logger.error(f"Unknown error: {error}")
