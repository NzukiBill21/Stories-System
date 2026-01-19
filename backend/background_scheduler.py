"""Background scheduler for automatic scraping based on source settings."""
import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from services import scrape_source
from models import Source
from loguru import logger


class BackgroundScheduler:
    """Background scheduler that scrapes sources based on their scrape_frequency_minutes."""
    
    def __init__(self, check_interval_minutes: int = 1):
        """
        Initialize the scheduler.
        
        Args:
            check_interval_minutes: How often to check if sources need scraping (default: 1 minute)
        """
        self.check_interval_minutes = check_interval_minutes
        self.running = False
        self.thread = None
        self.last_check = {}
    
    def _should_scrape(self, db: Session, source: Source) -> bool:
        """
        Check if a source should be scraped based on its scrape_frequency_minutes.
        
        Args:
            db: Database session
            source: Source to check
        
        Returns:
            True if source should be scraped, False otherwise
        """
        # If scrape_frequency_minutes is None, use default of 30 minutes
        frequency = source.scrape_frequency_minutes if source.scrape_frequency_minutes is not None else 30
        
        # If never checked, scrape it
        if not source.last_checked_at:
            return True
        
        # Calculate time since last check
        now = datetime.utcnow()
        time_since_last_check = (now - source.last_checked_at).total_seconds() / 60
        
        # Check if enough time has passed
        return time_since_last_check >= frequency
    
    def _scrape_sources(self):
        """Scrape all sources that need scraping."""
        db = SessionLocal()
        try:
            # Get all active sources
            sources = db.query(Source).filter(Source.is_active == True).all()
            
            sources_to_scrape = []
            for source in sources:
                if self._should_scrape(db, source):
                    sources_to_scrape.append(source)
            
            if not sources_to_scrape:
                return
            
            logger.info(f"Auto-scraping {len(sources_to_scrape)} sources...")
            
            for source in sources_to_scrape:
                try:
                    logger.info(f"Auto-scraping {source.platform}: {source.account_name} (frequency: {source.scrape_frequency_minutes} min)")
                    result = scrape_source(db, source.id)
                    posts = result.get('posts_fetched', 0)
                    stories = result.get('stories_created', 0)
                    logger.info(f"  ✓ {source.account_name}: {posts} posts, {stories} stories")
                except Exception as e:
                    logger.error(f"Error auto-scraping {source.account_name}: {e}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error in background scheduler: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _run(self):
        """Main scheduler loop."""
        logger.info(f"Background scheduler started (checking every {self.check_interval_minutes} minute(s))")
        
        while self.running:
            try:
                self._scrape_sources()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
            # Sleep for check interval
            time.sleep(self.check_interval_minutes * 60)
    
    def start(self):
        """Start the background scheduler."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Background scheduler started")
    
    def stop(self):
        """Stop the background scheduler."""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Background scheduler stopped")


# Global scheduler instance
_scheduler = None


def get_scheduler() -> BackgroundScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(check_interval_minutes=1)
    return _scheduler


def start_background_scheduler():
    """Start the background scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_background_scheduler():
    """Stop the background scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()
