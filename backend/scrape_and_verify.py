"""Scrape all active sources and verify data is created."""
from database import SessionLocal, test_connection
from models import Source, RawPost, Story
from services import scrape_source
from loguru import logger
import sys

def main():
    """Scrape all sources and verify data."""
    print("=" * 60)
    print("Scrape All Sources & Verify Data")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    print("[OK] Database connected\n")
    
    db = SessionLocal()
    try:
        # Get active sources
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        if not sources:
            print("[ERROR] No active sources found")
            print("Run: python setup_trending_sources.py")
            return 1
        
        print(f"Found {len(sources)} active source(s):\n")
        for source in sources:
            print(f"  - {source.platform}: {source.account_name or source.account_handle}")
        
        print("\n" + "=" * 60)
        print("Starting Scraping...")
        print("=" * 60)
        print()
        
        total_posts = 0
        total_stories = 0
        
        for source in sources:
            print(f"Scraping {source.platform} ({source.account_handle})...")
            try:
                result = scrape_source(db, source.id)
                posts = result.get('posts_fetched', 0)
                stories = result.get('stories_created', 0)
                total_posts += posts
                total_stories += stories
                
                if posts > 0:
                    print(f"  [OK] Fetched {posts} posts, created {stories} stories")
                else:
                    print(f"  [INFO] No posts found")
                    if source.platform == "Facebook":
                        print(f"         (User profile may be empty or private)")
                    elif source.platform == "TikTok":
                        print(f"         (TikTok API may need configuration)")
                    
            except Exception as e:
                logger.error(f"Error scraping {source.platform}: {e}")
                print(f"  [ERROR] {e}")
        
        # Verify data
        print("\n" + "=" * 60)
        print("Verifying Data...")
        print("=" * 60)
        print()
        
        raw_posts_count = db.query(RawPost).count()
        stories_count = db.query(Story).count()
        
        print(f"Raw posts in database: {raw_posts_count}")
        print(f"Stories in database: {stories_count}")
        
        if stories_count > 0:
            recent = db.query(Story).order_by(Story.created_at.desc()).limit(5).all()
            print(f"\nRecent stories:")
            for story in recent:
                print(f"  - {story.platform}: {story.title[:60] if story.title else story.content[:60]}...")
                print(f"    Score: {story.score:.1f}, Engagement: {story.engagement_velocity:.1f}/hr")
        else:
            print("\n[WARNING] No stories created")
            print("Possible reasons:")
            print("  1. No posts found from sources")
            print("  2. Posts don't meet engagement thresholds")
            print("  3. Scraping failed (check logs)")
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"\nPosts fetched this run: {total_posts}")
        print(f"Stories created this run: {total_stories}")
        print(f"Total stories in database: {stories_count}")
        
        if stories_count > 0:
            print("\n[OK] Data is ready for dashboard!")
            print("Start API: python main.py")
            print("View dashboard: http://localhost:3000")
        else:
            print("\n[INFO] No stories yet - this is normal if:")
            print("  - Sources have no posts")
            print("  - Posts don't meet engagement thresholds")
            print("  - Scraping needs configuration")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
