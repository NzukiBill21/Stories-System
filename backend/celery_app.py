"""Celery configuration and tasks for scheduled scraping."""
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from services import scrape_source
from hashtag_scraper import scrape_hashtag
from trend_aggregator import scrape_and_store_trends
from models import Source, Hashtag
from config import settings
from loguru import logger

# Create Celery app
celery_app = Celery(
    "story_intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name="scrape_source_task")
def scrape_source_task(source_id: int):
    """
    Celery task to scrape a single source.
    
    Args:
        source_id: ID of the source to scrape
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting scrape task for source {source_id}")
        result = scrape_source(db, source_id)
        logger.info(f"Scrape task completed for source {source_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in scrape task for source {source_id}: {e}")
        return {"error": str(e), "posts_fetched": 0}
    finally:
        db.close()


@celery_app.task(name="scrape_all_active_sources")
def scrape_all_active_sources():
    """
    Celery task to scrape all active sources.
    
    For Facebook: Aggregates trends from multiple Pages
    For other platforms: Scrapes individually
    """
    db = SessionLocal()
    try:
        # Separate Facebook Pages from other sources
        facebook_pages = db.query(Source).filter(
            Source.platform == "Facebook",
            Source.is_active == True,
            Source.account_id.isnot(None)  # Must have Page ID
        ).all()
        
        other_sources = db.query(Source).filter(
            Source.is_active == True,
            ~Source.platform.in_(["Facebook"])  # Exclude Facebook (handled separately)
        ).all()
        
        # Aggregate Facebook trends from multiple Pages
        facebook_result = None
        if facebook_pages:
            logger.info(f"Aggregating Facebook trends from {len(facebook_pages)} Pages")
            try:
                facebook_result = scrape_and_store_trends(
                    db=db,
                    page_sources=facebook_pages,
                    posts_per_page=10,
                    top_n=50,
                    min_trend_score=10.0
                )
                logger.info(f"Facebook trends: {facebook_result.get('posts_stored', 0)} posts stored")
            except Exception as e:
                logger.error(f"Error aggregating Facebook trends: {e}")
        
        # Scrape other platforms (TikTok, etc.)
        other_results = []
        for source in other_sources:
            # Check if it's time to scrape this source
            if source.last_checked_at:
                time_since_last_check = (
                    db.query(func.now()).scalar() - source.last_checked_at
                ).total_seconds() / 60
                
                if time_since_last_check < source.scrape_frequency_minutes:
                    logger.info(f"Skipping {source.account_handle} - not time yet")
                    continue
            
            result = scrape_source(db, source.id)
            other_results.append(result)
        
        logger.info(f"Scrape all task completed: {len(other_results)} other sources processed")
        return {
            "facebook_pages_scraped": len(facebook_pages),
            "facebook_result": facebook_result,
            "other_sources_processed": len(other_results),
            "other_results": other_results
        }
    except Exception as e:
        logger.error(f"Error in scrape all task: {e}")
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="scrape_all_active_hashtags")
def scrape_all_active_hashtags():
    """
    Celery task to scrape all active hashtags.
    """
    db = SessionLocal()
    try:
        hashtags = db.query(Hashtag).filter(Hashtag.is_active == True).all()
        logger.info(f"Starting scrape task for {len(hashtags)} active hashtags")
        
        results = []
        for hashtag in hashtags:
            # Check if it's time to scrape this hashtag
            if hashtag.last_scraped_at:
                from sqlalchemy import func
                time_since_last_check = (
                    db.query(func.now()).scalar() - hashtag.last_scraped_at
                ).total_seconds() / 60
                
                # Scrape hashtags every 30 minutes
                if time_since_last_check < 30:
                    logger.info(f"Skipping #{hashtag.hashtag} - not time yet")
                    continue
            
            result = scrape_hashtag(db, hashtag.id)
            results.append(result)
        
        logger.info(f"Hashtag scrape task completed: {len(results)} hashtags processed")
        return {"hashtags_processed": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error in scrape all hashtags task: {e}")
        return {"error": str(e)}
    finally:
        db.close()


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'scrape-all-sources-every-15-minutes': {
        'task': 'scrape_all_active_sources',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'scrape-all-hashtags-every-30-minutes': {
        'task': 'scrape_all_active_hashtags',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

# You can also add per-source schedules dynamically
# Example: scrape specific high-priority sources more frequently
