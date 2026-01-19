"""FastAPI application with REST endpoints."""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db
from models import Story, Source
from services import get_trending_stories, scrape_source
from pydantic import BaseModel
from config import settings
from background_scheduler import get_scheduler
from loguru import logger

app = FastAPI(title="Story Intelligence Dashboard API", version="1.0.0")

# Start background scheduler when API app starts
@app.on_event("startup")
async def startup_event():
    """Start background scheduler when API starts."""
    try:
        from background_scheduler import start_background_scheduler
        start_background_scheduler()
        logger.info("Background scheduler started on API startup")
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API responses
class StoryResponse(BaseModel):
    """Story response model matching frontend Story interface."""
    id: str
    headline: str
    source: str
    platform: str
    engagement: int
    velocity: str
    reason: str
    timestamp: str
    credibility: int
    url: str
    
    class Config:
        from_attributes = True


class ScrapeResponse(BaseModel):
    """Response model for scrape operations."""
    success: bool
    posts_fetched: int
    posts_processed: int
    stories_created: int
    source: Optional[str] = None
    error: Optional[str] = None


def story_to_response(story: Story) -> StoryResponse:
    """Convert Story model to API response format."""
    # Determine velocity category
    if story.engagement_velocity >= 100:
        velocity = "high"
    elif story.engagement_velocity >= 50:
        velocity = "medium"
    else:
        velocity = "low"
    
    # Format timestamp
    timestamp = story.posted_at.strftime("%Y-%m-%d %H:%M") if story.posted_at else ""
    
    return StoryResponse(
        id=str(story.id),
        headline=story.headline or story.content[:100] if story.content else "",
        source=story.author,
        platform=story.platform,
        engagement=story.likes + story.comments + story.shares,
        velocity=velocity,
        reason=story.reason_flagged or "High engagement",
        timestamp=timestamp,
        credibility=int(story.credibility_score),  # Note: This is credibility score, not overall score
        url=story.url
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Story Intelligence Dashboard API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    scheduler = get_scheduler()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "auto_scraping": scheduler.running if scheduler else False
    }


@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get background scheduler status."""
    scheduler = get_scheduler()
    return {
        "running": scheduler.running if scheduler else False,
        "check_interval_minutes": scheduler.check_interval_minutes if scheduler else None
    }


@app.get("/api/stories", response_model=List[StoryResponse])
async def get_stories(
    limit: int = Query(50, ge=1, le=200),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    platform: Optional[str] = Query(None),
    hours_back: int = Query(24, ge=1, le=168),
    is_kenyan: Optional[bool] = Query(None),
    location: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get trending stories.
    
    Args:
        limit: Maximum number of stories to return
        min_score: Minimum score threshold
        platform: Filter by platform (X, Facebook, Instagram, TikTok, Reddit, RSS)
        hours_back: Only get stories from last N hours
        db: Database session
    """
    stories = get_trending_stories(
        db=db,
        limit=limit,
        min_score=min_score,
        platform=platform,
        hours_back=hours_back,
        is_kenyan=is_kenyan,
        location=location,
        topic=topic
    )
    
    return [story_to_response(story) for story in stories]


@app.get("/api/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int, db: Session = Depends(get_db)):
    """Get a single story by ID."""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story_to_response(story)


@app.post("/api/scrape/{source_id}", response_model=ScrapeResponse)
async def scrape_source_endpoint(source_id: int, db: Session = Depends(get_db)):
    """
    Trigger scraping for a specific source.
    
    Args:
        source_id: ID of the source to scrape
        db: Database session
    """
    result = scrape_source(db, source_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ScrapeResponse(**result)


@app.get("/api/sources")
async def get_sources(
    is_kenyan: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all active sources."""
    query = db.query(Source).filter(Source.is_active == True)
    
    if is_kenyan is not None:
        query = query.filter(Source.is_kenyan == is_kenyan)
    
    sources = query.all()
    return [
        {
            "id": source.id,
            "platform": source.platform,
            "account_handle": source.account_handle,
            "account_name": source.account_name,
            "is_trusted": source.is_trusted,
            "is_kenyan": source.is_kenyan,
            "location": source.location,
            "last_checked_at": source.last_checked_at.isoformat() if source.last_checked_at else None
        }
        for source in sources
    ]


@app.post("/api/scrape/facebook-trends")
async def scrape_facebook_trends_endpoint(
    posts_per_page: int = Query(10, ge=1, le=50),
    top_n: int = Query(50, ge=1, le=200),
    min_trend_score: float = Query(10.0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Aggregate Facebook trends from multiple Pages.
    
    This endpoint:
    1. Fetches posts from all active Facebook Pages
    2. Computes trend_score = (likes + comments + shares) / minutes_since_posted
    3. Ranks by trend_score DESC
    4. Stores top N trending posts in raw_posts
    
    Args:
        posts_per_page: Number of posts to fetch per page
        top_n: Number of top trending posts to keep
        min_trend_score: Minimum trend score threshold
        db: Database session
    """
    from models import Source
    from trend_aggregator import scrape_and_store_trends
    
    # Get all active Facebook Pages
    facebook_pages = db.query(Source).filter(
        Source.platform == "Facebook",
        Source.is_active == True,
        Source.account_id.isnot(None)  # Must have Page ID
    ).all()
    
    if not facebook_pages:
        raise HTTPException(
            status_code=400,
            detail="No active Facebook Pages found. Add Pages using add_facebook_pages.py"
        )
    
    # Aggregate trends
    result = scrape_and_store_trends(
        db=db,
        page_sources=facebook_pages,
        posts_per_page=posts_per_page,
        top_n=top_n,
        min_trend_score=min_trend_score
    )
    
    return result


@app.get("/api/hashtags")
async def get_hashtags(
    is_kenyan: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all active hashtags."""
    from models import Hashtag
    
    query = db.query(Hashtag).filter(Hashtag.is_active == True)
    
    if is_kenyan is not None:
        query = query.filter(Hashtag.is_kenyan == is_kenyan)
    
    hashtags = query.all()
    return [
        {
            "id": hashtag.id,
            "hashtag": hashtag.hashtag,
            "platform": hashtag.platform,
            "is_kenyan": hashtag.is_kenyan,
            "last_scraped_at": hashtag.last_scraped_at.isoformat() if hashtag.last_scraped_at else None
        }
        for hashtag in hashtags
    ]


@app.post("/api/scrape/hashtag/{hashtag_id}")
async def scrape_hashtag_endpoint(hashtag_id: int, db: Session = Depends(get_db)):
    """Trigger scraping for a specific hashtag."""
    from hashtag_scraper import scrape_hashtag
    
    result = scrape_hashtag(db, hashtag_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.get("/api/insights")
async def get_insights(
    hours_back: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    Get insights and analytics data.
    
    Args:
        hours_back: Time range for insights
        db: Database session
    """
    time_threshold = datetime.utcnow() - timedelta(hours=hours_back)
    
    # Get stories in time range
    stories = db.query(Story).filter(
        Story.is_active == True,
        Story.posted_at >= time_threshold
    ).all()
    
    # Calculate topic clusters
    topic_counts = {}
    for story in stories:
        topic = story.topic or "General"
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    # Get trending topics (top 5)
    trending_topics = sorted(
        topic_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    # Calculate platform distribution
    platform_counts = {}
    for story in stories:
        platform = story.platform
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    # Calculate velocity distribution
    high_velocity = sum(1 for s in stories if s.engagement_velocity >= 100)
    medium_velocity = sum(1 for s in stories if 50 <= s.engagement_velocity < 100)
    low_velocity = sum(1 for s in stories if s.engagement_velocity < 50)
    
    # Get top keywords from story headlines
    keywords = {}
    for story in stories:
        if story.headline:
            words = story.headline.lower().split()
            for word in words:
                if len(word) > 4:  # Only meaningful words
                    keywords[word] = keywords.get(word, 0) + 1
    
    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_stories": len(stories),
        "high_velocity": high_velocity,
        "medium_velocity": medium_velocity,
        "low_velocity": low_velocity,
        "trending_topics": [
            {"name": topic, "count": count}
            for topic, count in trending_topics
        ],
        "platform_distribution": platform_counts,
        "top_keywords": [
            {"keyword": word, "mentions": count}
            for word, count in top_keywords
        ],
        "topic_clusters": [
            {
                "topic": topic,
                "count": count,
                "velocity": "rising" if count > len(stories) / len(topic_counts) else "stable",
                "keywords": [word for word, _ in top_keywords[:3]]
            }
            for topic, count in trending_topics
        ]
    }
