"""Database models for Story Intelligence Dashboard."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime


class Source(Base):
    """Social media sources/accounts to monitor."""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # X, Facebook, Instagram, TikTok
    account_handle = Column(String(255), nullable=False)  # @username or page name
    account_name = Column(String(255))  # Display name
    account_id = Column(String(255))  # Platform-specific ID
    is_active = Column(Boolean, default=True)
    is_trusted = Column(Boolean, default=False)  # High credibility source
    is_kenyan = Column(Boolean, default=False)  # Kenyan source flag
    location = Column(String(255))  # Location filter (e.g., "Nairobi", "Kenya")
    scrape_frequency_minutes = Column(Integer, default=15)  # How often to check
    last_checked_at = Column(DateTime)  # MySQL doesn't support timezone=True
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    raw_posts = relationship("RawPost", back_populates="source")
    
    __table_args__ = (
        Index('idx_source_platform_handle', 'platform', 'account_handle'),
        Index('idx_source_kenyan', 'is_kenyan'),
    )


class Hashtag(Base):
    """Hashtags to track for trending content."""
    __tablename__ = "hashtags"
    
    id = Column(Integer, primary_key=True, index=True)
    hashtag = Column(String(255), nullable=False, unique=True)  # e.g., "#KenyaElections"
    platform = Column(String(50), default="all")  # "all", "X", "Instagram", etc.
    is_kenyan = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    posts_per_hashtag = Column(Integer, default=20)  # How many posts to fetch per scrape
    min_engagement = Column(Integer, default=100)  # Minimum engagement threshold
    last_scraped_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_hashtag_platform', 'platform', 'is_active'),
    )


class RawPost(Base):
    """Raw posts fetched from social media platforms."""
    __tablename__ = "raw_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)  # Nullable for hashtag-based posts
    hashtag_id = Column(Integer, ForeignKey("hashtags.id"), nullable=True)  # If fetched via hashtag
    platform_post_id = Column(String(255), nullable=False)  # Platform-specific post ID
    platform = Column(String(50), nullable=False)
    author = Column(String(255), nullable=False)
    content = Column(Text)  # Post text/caption
    url = Column(String(500), nullable=False)
    posted_at = Column(DateTime, nullable=False)  # MySQL doesn't support timezone=True
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)  # Retweets for X, Shares for Facebook
    views = Column(Integer, default=0)
    
    # Location and geotag data
    location = Column(String(255))  # Extracted location/geotag
    is_kenyan = Column(Boolean, default=False)  # Flag if Kenyan content
    
    # Media
    media_url = Column(String(500))  # URL to image/video
    
    # Metadata
    raw_data = Column(Text)  # JSON string of raw API response
    fetched_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    source = relationship("Source", back_populates="raw_posts")
    hashtag = relationship("Hashtag", backref="raw_posts")
    story = relationship("Story", back_populates="raw_post", uselist=False)
    
    __table_args__ = (
        Index('idx_raw_post_platform_id', 'platform', 'platform_post_id'),
        Index('idx_raw_post_posted_at', 'posted_at'),
        Index('idx_raw_post_location', 'location'),
        Index('idx_raw_post_kenyan', 'is_kenyan'),
    )


class Story(Base):
    """Scored, filtered, and normalized stories ready for dashboard."""
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_post_id = Column(Integer, ForeignKey("raw_posts.id"), unique=True, nullable=False)
    
    # Normalized fields matching frontend Story interface
    platform = Column(String(50), nullable=False)
    author = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(500), nullable=False)
    posted_at = Column(DateTime, nullable=False)  # MySQL doesn't support timezone=True
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Scoring
    score = Column(Float, nullable=False)  # Overall score (0-100)
    engagement_velocity = Column(Float)  # Likes/hour or similar metric
    credibility_score = Column(Float, default=0.0)  # Based on source trust
    topic_relevance_score = Column(Float, default=0.0)  # Based on trending keywords
    
    # Location and Kenyan content
    location = Column(String(255))  # Location if available
    is_kenyan = Column(Boolean, default=False)  # Kenyan content flag
    
    # Frontend-compatible fields
    headline = Column(String(500))  # Extracted or generated headline
    reason_flagged = Column(String(255))  # Why this story was flagged
    topic = Column(String(255))  # Topic/category (politics, entertainment, etc.)
    
    # Status
    is_active = Column(Boolean, default=True)  # Still trending?
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    raw_post = relationship("RawPost", back_populates="story")
    
    __table_args__ = (
        Index('idx_story_score', 'score'),
        Index('idx_story_posted_at', 'posted_at'),
        Index('idx_story_active', 'is_active'),
        Index('idx_story_kenyan', 'is_kenyan'),
        Index('idx_story_location', 'location'),
    )


class ScrapeLog(Base):
    """Log table for tracking scraping operations."""
    __tablename__ = "scrape_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    hashtag_id = Column(Integer, ForeignKey("hashtags.id"), nullable=True)
    scrape_type = Column(String(50), default="source")  # "source", "hashtag", "location"
    status = Column(String(50), nullable=False)  # success, error, rate_limited
    posts_fetched = Column(Integer, default=0)
    posts_processed = Column(Integer, default=0)
    stories_created = Column(Integer, default=0)
    error_message = Column(Text)  # Error details if status is 'error'
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)  # Scraping duration
    
    # Relationships
    source = relationship("Source", backref="scrape_logs")
    hashtag = relationship("Hashtag", backref="scrape_logs")
    
    __table_args__ = (
        Index('idx_scrape_log_source', 'source_id'),
        Index('idx_scrape_log_hashtag', 'hashtag_id'),
        Index('idx_scrape_log_status', 'status'),
        Index('idx_scrape_log_started', 'started_at'),
    )
