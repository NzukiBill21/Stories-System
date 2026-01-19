"""Automated scraper for trending content - runs continuously."""
from database import SessionLocal
from models import Source
from services import scrape_source, process_post_to_story
from loguru import logger
import time
import sys
from datetime import datetime


def scrape_trending_sources():
    """Scrape all trending sources (RSS, Reddit, TikTok)."""
    db = SessionLocal()
    try:
        # Get all active trending sources (no auth required)
        trending_platforms = ['RSS', 'Reddit', 'TikTok', 'GoogleTrends']
        
        sources = db.query(Source).filter(
            Source.is_active == True,
            Source.platform.in_(trending_platforms)
        ).all()
        
        if not sources:
            logger.warning("No trending sources found. Run: python add_trending_sources.py")
            return 0
        
        logger.info(f"Found {len(sources)} trending sources to scrape")
        
        total_posts = 0
        total_stories = 0
        
        for source in sources:
            try:
                logger.info(f"Scraping {source.platform}: {source.account_name}")
                result = scrape_source(db, source.id)
                
                posts_fetched = result.get('posts_fetched', 0)
                stories_created = result.get('stories_created', 0)
                
                total_posts += posts_fetched
                total_stories += stories_created
                
                logger.info(
                    f"  ✓ {source.platform}: {posts_fetched} posts, "
                    f"{stories_created} stories"
                )
                
            except Exception as e:
                logger.error(f"Error scraping {source.platform} ({source.account_name}): {e}")
                continue
        
        # Process any remaining raw posts to stories
        from models import RawPost, Story
        unprocessed = db.query(RawPost).filter(
            ~RawPost.id.in_(
                db.query(Story.raw_post_id).filter(Story.raw_post_id.isnot(None))
            )
        ).limit(50).all()
        
        processed_count = 0
        for raw_post in unprocessed:
            try:
                story = process_post_to_story(db, raw_post)
                if story:
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing post {raw_post.id}: {e}")
                continue
        
        if processed_count > 0:
            logger.info(f"Processed {processed_count} additional posts to stories")
        
        db.commit()
        
        logger.info(
            f"Scraping complete: {total_posts} posts fetched, "
            f"{total_stories + processed_count} stories created"
        )
        
        return total_stories + processed_count
        
    except Exception as e:
        logger.error(f"Error in scraping: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    """Run automated trending scraper."""
    print("=" * 60)
    print("Automated Trending Content Scraper")
    print("=" * 60)
    print()
    print("This scraper pulls trending content from:")
    print("  - RSS feeds (BBC, CNN, Reuters, Kenyan news)")
    print("  - Reddit (worldnews, news, Kenya, technology)")
    print("  - TikTok (trending videos)")
    print()
    print("No authentication required!")
    print()
    
    # Run once immediately
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scrape...")
    stories_created = scrape_trending_sources()
    
    if stories_created > 0:
        print(f"\n[SUCCESS] Created {stories_created} trending stories!")
        print("\nStories are now available in your dashboard.")
    else:
        print("\n[WARNING] No new stories created. This could mean:")
        print("  - Sources need to be added (run: python add_trending_sources.py)")
        print("  - Content doesn't meet engagement thresholds")
        print("  - Sources are being rate-limited")
    
    print("\n" + "=" * 60)
    print("Scraping complete!")
    print("=" * 60)
    print("\nTo run continuously, use Celery Beat or schedule this script.")
    print("To run again manually: python auto_scrape_trending.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
