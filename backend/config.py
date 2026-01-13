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
    tiktok_trending_limit: int = 50  # Number of trending videos to fetch per run
    tiktok_min_engagement_velocity: float = 100.0  # Minimum engagement per minute
    
    # Scraping
    scraping_enabled: bool = True
    rate_limit_delay: float = 1.0
    
    # Scoring thresholds
    min_engagement_score: int = 50
    min_engagement_velocity: float = 10.0  # likes/hour
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Trusted sources (high credibility accounts)
    trusted_sources: List[str] = [
        # Add trusted account handles here
        # Example: "@BBCNews", "@CNN", "@Reuters"
    ]
    
    # Trending keywords (for topic relevance scoring)
    trending_keywords: List[str] = [
        # Global keywords
        "breaking", "election", "crisis", "announcement",
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
