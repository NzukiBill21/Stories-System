"""Configuration settings for the Story Intelligence Dashboard backend."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - MySQL connection parameters
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "story_intelligence"
    
    # Database URL (constructed from above, or can be set directly)
    database_url: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Twitter/X API
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    
    # Facebook API
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    facebook_access_token: str = ""
    
    # Instagram API
    instagram_access_token: str = ""
    
    # TikTok Configuration
    tiktok_trending_limit: int = 100  # Number of trending videos to fetch per run (increased for more content)
    tiktok_min_engagement_velocity: float = 50.0  # Minimum engagement per minute (lowered to catch more trending content)
    
    # Scraping
    scraping_enabled: bool = True
    rate_limit_delay: float = 1.0
    
    # Scoring thresholds
    min_engagement_score: int = 30  # Lowered to catch more trending content
    min_engagement_velocity: float = 5.0  # Lowered to catch more trending content (likes/hour)
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8001  # Changed to avoid conflict with other API
    
    # Trusted sources (high credibility accounts)
    trusted_sources: List[str] = [
        # Add trusted account handles here
        # Example: "@BBCNews", "@CNN", "@Reuters"
    ]
    
    # Trending keywords (for topic relevance scoring)
    trending_keywords: List[str] = [
        # Global trending keywords
        "breaking", "election", "crisis", "announcement", "scandal", "protest",
        "viral", "trending", "shocking", "exclusive", "investigation", "revealed",
        "outrage", "controversy", "resignation", "arrest", "court", "verdict",
        "emergency", "disaster", "accident", "fire", "flood", "earthquake",
        "pandemic", "outbreak", "health", "medical", "vaccine", "treatment",
        "technology", "innovation", "launch", "release", "update", "hack",
        "celebration", "victory", "champion", "award", "record", "achievement",
        "politics", "government", "policy", "law", "bill", "vote",
        "economy", "market", "stock", "business", "trade", "finance",
        "sports", "match", "game", "tournament", "championship", "win",
        "entertainment", "movie", "music", "celebrity", "premiere", "awards",
        # Kenyan keywords (will be merged with kenyan_sources_config)
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_database_url(self) -> str:
        """Construct MySQL database URL from individual parameters."""
        if self.database_url:
            return self.database_url
        
        # Build MySQL connection string
        # Handle empty password - use empty string explicitly
        password = self.db_password if self.db_password else ""
        # Format: mysql+pymysql://user:password@host:port/database
        return f"mysql+pymysql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"


settings = Settings()
