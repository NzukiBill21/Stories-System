"""Test trending content scraping - Facebook user profile and TikTok trending."""
from database import SessionLocal
from models import Source
from services import scrape_source
from loguru import logger

def main():
    """Test scraping trending content."""
    print("=" * 60)
    print("Testing Trending Content Scraping")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Get active sources
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        print(f"Found {len(sources)} active source(s):\n")
        for source in sources:
            print(f"  {source.platform}: {source.account_name}")
            print(f"    Handle: {source.account_handle}")
            if source.account_id:
                print(f"    ID: {source.account_id}")
            print()
        
        print("Starting scraping...\n")
        
        total_posts = 0
        total_stories = 0
        
        for source in sources:
            print(f"Scraping {source.platform}...")
            try:
                result = scrape_source(db, source.id)
                posts = result.get('posts_fetched', 0)
                stories = result.get('stories_created', 0)
                total_posts += posts
                total_stories += stories
                
                if posts > 0:
                    print(f"  [OK] Fetched {posts} posts, created {stories} stories")
                else:
                    print(f"  [INFO] No posts found (may be empty or need different endpoint)")
                    
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"  [ERROR] {e}")
        
        print("\n" + "=" * 60)
        print("SCRAPING SUMMARY")
        print("=" * 60)
        print(f"\nTotal posts fetched: {total_posts}")
        print(f"Total stories created: {total_stories}")
        
        # Show platforms available
        from models import Story
        platforms = db.query(Story.platform).distinct().all()
        if platforms:
            print(f"\nPlatforms with stories: {[p[0] for p in platforms]}")
        
        print("\n" + "=" * 60)
        print("SYSTEM READY!")
        print("=" * 60)
        print("\nPlatforms configured:")
        print("  - TikTok: Trending videos (high engagement)")
        print("  - Facebook: User profile posts")
        print("\nStart API: python main.py")
        print("View dashboard: http://localhost:3000")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    sys.exit(main())
