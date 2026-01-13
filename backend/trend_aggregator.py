"""
Facebook Trends Aggregator - Computes trends from multiple Pages.

Facebook has no trending endpoint. Trends must be computed via:
1. Aggregate posts from multiple public Pages
2. Calculate trend_score = (likes + comments + shares) / minutes_since_posted
3. Rank by trend_score DESC
4. Keep top N (e.g., 20-50)

This is how real media monitoring platforms work.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models import Source, RawPost
from platforms.facebook import FacebookScraper
from loguru import logger


def calculate_trend_score(
    likes: int,
    comments: int,
    shares: int,
    posted_at: datetime,
    current_time: Optional[datetime] = None
) -> float:
    """
    Calculate trend score: (likes + comments + shares) / minutes_since_posted
    
    This is the core metric for Facebook trends - engagement velocity.
    Higher score = more trending.
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    # Calculate time difference in minutes
    time_diff = current_time - posted_at.replace(tzinfo=None) if posted_at.tzinfo else current_time - posted_at
    minutes_elapsed = max(time_diff.total_seconds() / 60, 0.1)  # At least 0.1 minutes to avoid division by zero
    
    # Total engagement
    total_engagement = likes + comments + shares
    
    # Trend score = engagement per minute
    trend_score = total_engagement / minutes_elapsed
    
    return trend_score


def aggregate_facebook_trends(
    db: Session,
    page_sources: List[Source],
    posts_per_page: int = 10,
    top_n: int = 50,
    min_trend_score: float = 10.0
) -> List[Dict]:
    """
    Aggregate posts from multiple Facebook Pages and compute trends.
    
    Args:
        db: Database session
        page_sources: List of Facebook Page sources to aggregate
        posts_per_page: Number of posts to fetch per page
        top_n: Number of top trending posts to return
        min_trend_score: Minimum trend score threshold
    
    Returns:
        List of trending posts sorted by trend_score DESC
    """
    logger.info(f"Aggregating Facebook trends from {len(page_sources)} Pages")
    
    scraper = FacebookScraper()
    all_posts = []
    current_time = datetime.utcnow()
    
    # Fetch posts from all pages
    for source in page_sources:
        if not source.is_active:
            continue
        
        if not source.account_id:
            logger.warning(f"Skipping {source.account_handle} - no Page ID (account_id)")
            continue
        
        try:
            posts = scraper.fetch_posts(source, limit=posts_per_page)
            
            # Calculate trend score for each post
            for post in posts:
                trend_score = calculate_trend_score(
                    likes=post.get('likes', 0),
                    comments=post.get('comments', 0),
                    shares=post.get('shares', 0),
                    posted_at=post.get('posted_at'),
                    current_time=current_time
                )
                
                # Add trend score to post data
                post['trend_score'] = trend_score
                post['source_id'] = source.id
                post['source_name'] = source.account_name or source.account_handle
                
                all_posts.append(post)
            
            logger.info(f"Fetched {len(posts)} posts from {source.account_handle}")
            
        except Exception as e:
            logger.error(f"Error fetching posts from {source.account_handle}: {e}")
            continue
    
    # Filter by minimum trend score
    filtered_posts = [
        post for post in all_posts
        if post.get('trend_score', 0) >= min_trend_score
    ]
    
    # Sort by trend_score DESC
    sorted_posts = sorted(
        filtered_posts,
        key=lambda x: x.get('trend_score', 0),
        reverse=True
    )
    
    # Keep top N
    top_trending = sorted_posts[:top_n]
    
    logger.info(
        f"Aggregated {len(all_posts)} posts from {len(page_sources)} Pages. "
        f"Found {len(filtered_posts)} above threshold. "
        f"Returning top {len(top_trending)} trending posts."
    )
    
    return top_trending


def scrape_and_store_trends(
    db: Session,
    page_sources: Optional[List[Source]] = None,
    posts_per_page: int = 10,
    top_n: int = 50,
    min_trend_score: float = 10.0
) -> Dict:
    """
    Aggregate Facebook trends and store in database.
    
    This function:
    1. Aggregates posts from multiple Facebook Pages
    2. Computes trend scores
    3. Stores top trending posts in raw_posts
    4. Returns summary statistics
    
    Args:
        db: Database session
        page_sources: List of Facebook Page sources (if None, fetches all active Facebook Pages)
        posts_per_page: Number of posts to fetch per page
        top_n: Number of top trending posts to keep
        min_trend_score: Minimum trend score threshold
    
    Returns:
        Dictionary with summary statistics
    """
    if page_sources is None:
        # Get all active Facebook Pages
        page_sources = db.query(Source).filter(
            Source.platform == "Facebook",
            Source.is_active == True,
            Source.account_id.isnot(None)  # Must have Page ID
        ).all()
    
    if not page_sources:
        logger.warning("No active Facebook Pages found for trend aggregation")
        return {
            "error": "No active Facebook Pages found",
            "posts_fetched": 0,
            "posts_stored": 0,
            "top_trending": 0
        }
    
    # Aggregate trends
    trending_posts = aggregate_facebook_trends(
        db=db,
        page_sources=page_sources,
        posts_per_page=posts_per_page,
        top_n=top_n,
        min_trend_score=min_trend_score
    )
    
    # Store in database
    posts_stored = 0
    for post_data in trending_posts:
        try:
            # Check if post already exists
            existing = db.query(RawPost).filter(
                RawPost.platform == "Facebook",
                RawPost.platform_post_id == post_data.get('platform_post_id')
            ).first()
            
            if existing:
                continue  # Skip duplicates
            
            # Get source
            source = db.query(Source).filter(Source.id == post_data.get('source_id')).first()
            if not source:
                continue
            
            # Create RawPost
            raw_post = RawPost(
                source_id=source.id,
                platform_post_id=post_data.get('platform_post_id'),
                platform="Facebook",
                author=post_data.get('author', source.account_name),
                content=post_data.get('content', ''),
                url=post_data.get('url', ''),
                posted_at=post_data.get('posted_at'),
                likes=post_data.get('likes', 0),
                comments=post_data.get('comments', 0),
                shares=post_data.get('shares', 0),
                views=post_data.get('views', 0),
                raw_data=post_data.get('raw_data', '{}')
            )
            
            db.add(raw_post)
            posts_stored += 1
            
        except Exception as e:
            logger.error(f"Error storing post {post_data.get('platform_post_id')}: {e}")
            continue
    
    try:
        db.commit()
        logger.info(f"Stored {posts_stored} trending posts in database")
    except Exception as e:
        logger.error(f"Error committing posts: {e}")
        db.rollback()
        posts_stored = 0
    
    return {
        "success": True,
        "posts_fetched": len(trending_posts),
        "posts_stored": posts_stored,
        "top_trending": len(trending_posts),
        "pages_scraped": len(page_sources)
    }
