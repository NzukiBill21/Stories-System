"""Base class for platform scrapers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from models import RawPost, Source


class PlatformScraper(ABC):
    """Base class for all platform scrapers."""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
    
    @abstractmethod
    def fetch_posts(
        self,
        source: Source,
        limit: int = 50
    ) -> List[Dict]:
        """
        Fetch posts from the platform for a given source.
        
        Args:
            source: Source object to fetch posts for
            limit: Maximum number of posts to fetch
        
        Returns:
            List of post dictionaries with standardized fields
        """
        pass
    
    @abstractmethod
    def normalize_post(self, raw_data: Dict, source: Source) -> Dict:
        """
        Normalize platform-specific post data to standard format.
        
        Args:
            raw_data: Raw post data from platform API
            source: Source object
        
        Returns:
            Normalized post dictionary with fields:
            - platform_post_id
            - platform
            - author
            - content
            - url
            - posted_at
            - likes
            - comments
            - shares
            - views
            - raw_data (JSON string)
        """
        pass
    
    def handle_rate_limit(self, error: Exception) -> None:
        """
        Handle rate limiting errors.
        
        Args:
            error: The rate limit exception
        """
        # Default implementation - can be overridden
        import time
        from config import settings
        time.sleep(settings.rate_limit_delay * 10)  # Wait longer on rate limit
    
    def handle_error(self, error: Exception, source: Source) -> None:
        """
        Handle general errors during scraping.
        
        Args:
            error: The exception
            source: Source that was being scraped
        """
        from loguru import logger
        logger.error(f"Error fetching posts for {source.account_handle} on {self.platform_name}: {error}")
