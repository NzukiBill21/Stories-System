"""Trigger scraping and show results immediately."""
from database import SessionLocal
from models import Source
from services import scrape_source, process_post_to_story
from loguru import logger
import sys

def main():
    """Scrape and show results."""
    print("=" * 60)
    print("Scraping Facebook & TikTok")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Get active sources
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        if not sources:
            print("[ERROR] No active sources found")
            print("Run: python fix_all_issues.py")
            return 1
        
        print(f"Found {len(sources)} active source(s):")
        for source in sources:
            print(f"  - {source.platform}: {source.account_handle}")
        
        print("\nStarting scraping...\n")
        
        total_posts = 0
        total_stories = 0
        
        for source in sources:
            print(f"Scraping {source.platform} ({source.account_handle})...")
            try:
                result = scrape_source(db, source.id)
                posts_fetched = result.get('posts_fetched', 0)
                stories_created = result.get('stories_created', 0)
                total_posts += posts_fetched
                total_stories += stories_created
                print(f"  [OK] Fetched {posts_fetched} posts, created {stories_created} stories")
            except Exception as e:
                logger.error(f"Error scraping {source.platform}: {e}")
                print(f"  [ERROR] {e}")
        
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"\nTotal posts fetched: {total_posts}")
        print(f"Total stories created: {total_stories}")
        
        # Show recent stories
        from models import Story
        recent = db.query(Story).order_by(Story.created_at.desc()).limit(10).all()
        
        if recent:
            print(f"\nRecent stories ({len(recent)}):")
            for story in recent:
                print(f"\n  {story.platform} - Score: {story.score:.1f}")
                print(f"  Title: {story.title[:60]}...")
                print(f"  Engagement: {story.engagement_velocity:.1f}/hr")
                print(f"  URL: {story.url}")
        else:
            print("\n[INFO] No stories yet - posts may need more engagement")
        
        print("\n" + "=" * 60)
        print("DATA IS READY FOR DASHBOARD!")
        print("=" * 60)
        print("\nStart API server:")
        print("  python main.py")
        print("\nThen check dashboard at: http://localhost:3000")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
