"""Actually pull real content from platforms - focus on what users see."""
from database import SessionLocal, test_connection
from models import Source, RawPost, Story
from services import scrape_source
from platforms.facebook import FacebookScraper
from platforms.tiktok import TikTokScraper
from loguru import logger
import sys

def pull_facebook_public_posts():
    """Pull public posts that users can see."""
    print("=" * 60)
    print("Pulling Real Public Content")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    db = SessionLocal()
    try:
        # Get Facebook source
        fb_source = db.query(Source).filter(
            Source.platform == "Facebook",
            Source.is_active == True
        ).first()
        
        if not fb_source:
            print("[ERROR] No active Facebook source")
            return 1
        
        print(f"Scraping Facebook: {fb_source.account_name} (ID: {fb_source.account_id})")
        print("Attempting to fetch public posts...\n")
        
        # Try different endpoints for user profile
        scraper = FacebookScraper()
        
        # Try /feed endpoint (for user profiles)
        try:
            posts = scraper.fetch_posts(fb_source, limit=10)
            if posts:
                print(f"[OK] Found {len(posts)} posts!")
                for i, post in enumerate(posts[:3], 1):
                    print(f"\n  {i}. {post.get('content', 'No content')[:60]}...")
                    print(f"     Likes: {post.get('likes', 0)}, Comments: {post.get('comments', 0)}")
            else:
                print("[INFO] No posts found")
                print("This could mean:")
                print("  - User profile has no public posts")
                print("  - Posts are private")
                print("  - Need different permissions")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        # Process posts if found
        if posts:
            print(f"\nProcessing {len(posts)} posts...")
            result = scrape_source(db, fb_source.id)
            print(f"Created {result.get('stories_created', 0)} stories")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        return 1
    finally:
        db.close()

def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("PULL REAL CONTENT - What Users See")
    print("=" * 60)
    print("\nThis will attempt to pull actual public content")
    print("that users can see on Facebook and TikTok.\n")
    
    # Pull Facebook
    pull_facebook_public_posts()
    
    print("\n" + "=" * 60)
    print("NOTE")
    print("=" * 60)
    print("\nIf no posts found:")
    print("  1. User profile may be empty/private")
    print("  2. Need to add a Facebook Page (not user profile)")
    print("  3. Or configure different sources with public content")
    print("\nFor TikTok:")
    print("  - TikTok API needs proper configuration")
    print("  - May need session ID or different method")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
