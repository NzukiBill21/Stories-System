"""Scrape only Kenyan sources to get more local content."""
from database import SessionLocal
from models import Source
from services import scrape_source
from loguru import logger
import sys


def scrape_kenyan_sources():
    """Scrape all Kenyan sources."""
    db = SessionLocal()
    try:
        # Get all active Kenyan sources
        kenyan_sources = db.query(Source).filter(
            Source.is_kenyan == True,
            Source.is_active == True
        ).all()
        
        if not kenyan_sources:
            print("No Kenyan sources found")
            return 0
        
        print(f"Found {len(kenyan_sources)} Kenyan sources")
        print()
        
        total_posts = 0
        total_stories = 0
        
        for source in kenyan_sources:
            print(f"Scraping {source.platform}: {source.account_name}...")
            try:
                result = scrape_source(db, source.id)
                posts = result.get('posts_fetched', 0)
                stories = result.get('stories_created', 0)
                total_posts += posts
                total_stories += stories
                print(f"  ✓ {posts} posts, {stories} stories")
            except Exception as e:
                logger.error(f"Error scraping {source.account_name}: {e}")
                print(f"  ✗ Error: {e}")
        
        print()
        print("=" * 60)
        print(f"Total: {total_posts} posts, {total_stories} stories")
        print("=" * 60)
        
        return total_stories
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 0
    finally:
        db.close()


def main():
    """Scrape Kenyan sources."""
    print("=" * 60)
    print("Scraping Kenyan Sources Only")
    print("=" * 60)
    print()
    
    stories = scrape_kenyan_sources()
    
    print(f"\n[SUCCESS] Created {stories} Kenyan stories!")
    print("\nNow filter by 'Local (Kenya)' to see them.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
