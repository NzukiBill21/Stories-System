"""Service layer for processing posts and creating stories."""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional
import re
from models import Source, RawPost, Story, ScrapeLog
from platforms import get_scraper
from scoring import (
    calculate_engagement_velocity,
    calculate_credibility_score,
    calculate_topic_relevance_score,
    calculate_overall_score,
    should_keep_post
)
from trend_aggregator import scrape_and_store_trends
from loguru import logger


def scrape_source(db: Session, source_id: int) -> dict:
    """
    Scrape posts from a source and store them.
    
    Args:
        db: Database session
        source_id: ID of the source to scrape
    
    Returns:
        Dictionary with scraping results
    """
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return {"error": "Source not found", "posts_fetched": 0}
    
    if not source.is_active:
        return {"error": "Source is not active", "posts_fetched": 0}
    
    # Create scrape log entry
    scrape_start = datetime.utcnow()
    scrape_log = ScrapeLog(
        source_id=source.id,
        status="running",
        started_at=scrape_start
    )
    db.add(scrape_log)
    db.flush()
    
    try:
        # Get appropriate scraper
        scraper = get_scraper(source.platform)
        
        # Fetch posts
        raw_posts_data = scraper.fetch_posts(source, limit=50)
        
        posts_fetched = 0
        posts_processed = 0
        stories_created = 0
        
        for post_data in raw_posts_data:
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
                source_id=source.id,
                platform_post_id=post_data['platform_post_id'],
                platform=post_data['platform'],
                author=post_data['author'],
                content=post_data['content'],
                url=post_data['url'],
                posted_at=post_data['posted_at'],
                likes=post_data['likes'],
                comments=post_data['comments'],
                shares=post_data['shares'],
                views=post_data['views'],
                raw_data=post_data['raw_data'],
                # Inherit Kenyan flag and location from source or post_data
                is_kenyan=post_data.get('is_kenyan', source.is_kenyan if source else False),
                location=post_data.get('location', source.location if source else None)
            )
            
            db.add(raw_post)
            db.flush()  # Get the ID
            
            posts_fetched += 1
            
            # Process and score the post
            try:
                story = process_post_to_story(db, raw_post)
                if story:
                    posts_processed += 1
                    if should_keep_post(story.score, story.engagement_velocity):
                        stories_created += 1
                    else:
                        # Delete story if it doesn't meet threshold
                        db.delete(story)
                        db.flush()
            except Exception as e:
                logger.error(f"Error processing post {raw_post.id} to story: {e}")
                continue
        
        # Update source last_checked_at
        source.last_checked_at = datetime.utcnow()
        
        # Update scrape log with success
        scrape_end = datetime.utcnow()
        scrape_log.status = "success"
        scrape_log.posts_fetched = posts_fetched
        scrape_log.posts_processed = posts_processed
        scrape_log.stories_created = stories_created
        scrape_log.completed_at = scrape_end
        scrape_log.duration_seconds = (scrape_end - scrape_start).total_seconds()
        
        db.commit()
        
        return {
            "success": True,
            "posts_fetched": posts_fetched,
            "posts_processed": posts_processed,
            "stories_created": stories_created,
            "source": source.account_handle
        }
        
    except Exception as e:
        logger.error(f"Error scraping source {source.account_handle}: {e}")
        
        # Update scrape log with error
        scrape_end = datetime.utcnow()
        scrape_log.status = "error"
        scrape_log.error_message = str(e)
        scrape_log.completed_at = scrape_end
        scrape_log.duration_seconds = (scrape_end - scrape_start).total_seconds()
        scrape_log.posts_fetched = posts_fetched
        scrape_log.posts_processed = posts_processed
        scrape_log.stories_created = stories_created
        
        try:
            db.commit()
        except Exception as commit_error:
            logger.error(f"Error committing scrape log: {commit_error}")
            db.rollback()
        
        return {"error": str(e), "posts_fetched": 0}


def process_post_to_story(db: Session, raw_post: RawPost) -> Optional[Story]:
    """
    Process a raw post into a scored story.
    
    Args:
        db: Database session
        raw_post: Raw post to process
    
    Returns:
        Story object if created, None otherwise
    """
    try:
        # Calculate scores
        engagement_velocity = calculate_engagement_velocity(
            raw_post.likes,
            raw_post.comments,
            raw_post.shares,
            raw_post.views,
            raw_post.posted_at
        )
        
        credibility_score = calculate_credibility_score(
            raw_post.author,
            raw_post.source.is_trusted
        )
        
        topic_relevance_score = calculate_topic_relevance_score(
            raw_post.content or "",
            is_kenyan=raw_post.is_kenyan,
            location=raw_post.location
        )
        
        overall_score, reason_flagged = calculate_overall_score(
            engagement_velocity,
            credibility_score,
            topic_relevance_score,
            raw_post.likes,
            raw_post.comments,
            raw_post.shares,
            raw_post.views,
            is_kenyan=raw_post.is_kenyan,
            location=raw_post.location
        )
        
        # For Facebook trends, use "High engagement velocity" as reason
        if raw_post.platform == "Facebook" and engagement_velocity >= 10:
            reason_flagged = "High engagement velocity"
        
        # Generate headline (first 100 chars of content or author + platform)
        # Try to extract a meaningful headline from content
        content = raw_post.content or ""
        
        # Special handling for Google Trends - content should already be clean topic name
        if raw_post.platform == "GoogleTrends":
            # For Google Trends, the content IS the headline (trending topic name)
            headline = content.strip()
            # Remove any remaining artifacts
            headline = re.sub(r'\s+', ' ', headline)
            # If it contains "Trending search in", remove that part
            headline = re.sub(r'\s*Trending search in [A-Z]{2}\s*', '', headline, flags=re.I)
            headline = headline.strip()
        else:
            headline = content[:100].strip()
        
        # If content is too short or empty, create a descriptive headline
        if not headline or len(headline) < 3:
            headline = f"{raw_post.author} on {raw_post.platform}"
        else:
            # Clean up headline - remove extra whitespace, newlines
            headline = " ".join(headline.split())
            # If it's very long, truncate at word boundary
            if len(headline) > 100:
                headline = headline[:97] + "..."
        
        # Extract topic from content or hashtags
        topic = None
        content_lower = (raw_post.content or "").lower()
        if any(kw in content_lower for kw in ["politics", "election", "government"]):
            topic = "Politics"
        elif any(kw in content_lower for kw in ["entertainment", "music", "movie", "celebrity"]):
            topic = "Entertainment"
        elif any(kw in content_lower for kw in ["sports", "football", "cricket", "athletics"]):
            topic = "Sports"
        elif any(kw in content_lower for kw in ["tech", "technology", "innovation", "startup"]):
            topic = "Tech"
        else:
            topic = "General"
        
        # Check if story already exists for this raw_post
        existing_story = db.query(Story).filter(Story.raw_post_id == raw_post.id).first()
        if existing_story:
            # Update existing story
            existing_story.score = overall_score
            existing_story.engagement_velocity = engagement_velocity
            existing_story.credibility_score = credibility_score
            existing_story.topic_relevance_score = topic_relevance_score
            existing_story.headline = headline
            existing_story.reason_flagged = reason_flagged
            existing_story.topic = topic
            return existing_story
        
        # Create story
        story = Story(
            raw_post_id=raw_post.id,
            platform=raw_post.platform,
            author=raw_post.author,
            content=raw_post.content or "",
            url=raw_post.url,
            posted_at=raw_post.posted_at,
            likes=raw_post.likes,
            comments=raw_post.comments,
            shares=raw_post.shares,
            views=raw_post.views,
            score=overall_score,
            engagement_velocity=engagement_velocity,
            credibility_score=credibility_score,
            topic_relevance_score=topic_relevance_score,
            headline=headline,
            reason_flagged=reason_flagged,
            location=raw_post.location,
            is_kenyan=raw_post.is_kenyan,
            topic=topic
        )
        
        db.add(story)
        db.flush()  # Flush to ensure story is persisted
        return story
        
    except Exception as e:
        logger.error(f"Error processing post {raw_post.id} to story: {e}")
        return None


def get_trending_stories(
    db: Session,
    limit: int = 50,
    min_score: Optional[float] = None,
    platform: Optional[str] = None,
    hours_back: int = 24,
    is_kenyan: Optional[bool] = None,
    location: Optional[str] = None,
    topic: Optional[str] = None
) -> List[Story]:
    """
    Get trending stories from the database.
    
    Args:
        db: Database session
        limit: Maximum number of stories to return
        min_score: Minimum score threshold
        platform: Filter by platform
        hours_back: Only get stories from last N hours
    
    Returns:
        List of Story objects
    """
    query = db.query(Story).filter(Story.is_active == True)
    
    # Filter by time
    time_threshold = datetime.utcnow() - timedelta(hours=hours_back)
    query = query.filter(Story.posted_at >= time_threshold)
    
    # Filter by platform
    if platform:
        query = query.filter(Story.platform == platform)
    
    # Filter by minimum score
    if min_score:
        query = query.filter(Story.score >= min_score)
    
    # Filter by Kenyan content
    if is_kenyan is not None:
        query = query.filter(Story.is_kenyan == is_kenyan)
    
    # Filter by location (supports partial matches for "Africa", "Kenya", etc.)
    if location:
        # Case-insensitive location matching
        from sqlalchemy import func, or_
        location_lower = location.lower()
        
        # For "Africa" filter, match various African locations
        if location_lower == "africa":
            # Match stories with African locations or African countries
            # Also include Kenyan content (is_kenyan=True) as part of Africa
            african_locations = ['africa', 'kenya', 'nigeria', 'south africa', 'ghana', 
                               'tanzania', 'uganda', 'nairobi', 'mombasa', 'lagos', 
                               'johannesburg', 'cairo', 'accra', 'dar es salaam', 'kampala',
                               'kisumu', 'nakuru', 'eldoret']
            conditions = [
                func.lower(Story.location).contains(loc) 
                for loc in african_locations
            ]
            # Also include Kenyan stories even if location is not set
            conditions.append(Story.is_kenyan == True)
            query = query.filter(or_(*conditions))
        else:
            # Specific location match
            query = query.filter(
                func.lower(Story.location).contains(location_lower)
            )
    
    # Filter by topic
    if topic:
        query = query.filter(Story.topic == topic)
    
    # Order by score descending (prioritize trending content)
    # Prioritize high engagement velocity (trending content)
    # Then prioritize Kenyan content
    # Then by overall score
    query = query.order_by(
        Story.engagement_velocity.desc(),  # High engagement velocity first (trending)
        Story.is_kenyan.desc(),  # Kenyan second
        Story.score.desc(),  # Then by overall score
        Story.posted_at.desc()  # Most recent last (but still important)
    )
    
    return query.limit(limit).all()
