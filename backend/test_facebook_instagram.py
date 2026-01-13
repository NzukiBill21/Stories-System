"""Test script to verify Facebook and Instagram scrapers work with provided tokens."""
from platforms.facebook import FacebookScraper
from platforms.instagram import InstagramScraper
from models import Source
from database import SessionLocal, test_connection
from config import settings
from loguru import logger
import sys


def test_facebook():
    """Test Facebook scraper."""
    print("=" * 60)
    print("FACEBOOK SCRAPER TEST")
    print("=" * 60)
    print()
    
    # Check token
    if not settings.facebook_access_token:
        print("✗ Facebook access token not configured in .env")
        print("  Add: FACEBOOK_ACCESS_TOKEN=your_token")
        return False
    
    print(f"✓ Facebook token found: {settings.facebook_access_token[:20]}...")
    print()
    
    # Create test source (you'll need to replace with actual page ID)
    print("⚠ NOTE: Facebook requires a PAGE ID, not just a handle")
    print("  To get page ID:")
    print("  1. Go to https://developers.facebook.com/tools/explorer/")
    print("  2. Use your access token")
    print("  3. Query: GET /me/accounts")
    print("  4. Or use: GET /{page-name}?fields=id")
    print()
    
    test_source = Source(
        platform="Facebook",
        account_handle="BBCNews",  # Replace with actual page ID
        account_name="BBC News",
        account_id=None  # Set this to actual page ID
    )
    
    scraper = FacebookScraper()
    
    print(f"Testing Facebook scraper with page: {test_source.account_handle}")
    print("This may take a moment...\n")
    
    try:
        posts = scraper.fetch_posts(test_source, limit=5)
        
        if len(posts) == 0:
            print("⚠ No posts fetched")
            print("\nPossible reasons:")
            print("  - Page ID is incorrect (need numeric ID, not handle)")
            print("  - Access token doesn't have 'pages_read_engagement' permission")
            print("  - Page doesn't exist or is private")
            return False
        
        print(f"✓ Successfully fetched {len(posts)} posts!\n")
        
        # Show first post
        if posts:
            post = posts[0]
            print("Sample post:")
            print(f"  ID: {post['platform_post_id']}")
            print(f"  Content: {post['content'][:60]}...")
            print(f"  Likes: {post['likes']}, Comments: {post['comments']}, Shares: {post['shares']}")
            print(f"  URL: {post['url']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Facebook test error: {e}")
        return False


def test_instagram():
    """Test Instagram scraper."""
    print("\n" + "=" * 60)
    print("INSTAGRAM SCRAPER TEST")
    print("=" * 60)
    print()
    
    # Check token
    if not settings.instagram_access_token:
        print("✗ Instagram access token not configured in .env")
        print("  Add: INSTAGRAM_ACCESS_TOKEN=your_token")
        return False
    
    print(f"✓ Instagram token found: {settings.instagram_access_token[:20]}...")
    print()
    
    # Create test source (you'll need to replace with actual account ID)
    print("⚠ NOTE: Instagram requires an ACCOUNT ID, not just a handle")
    print("  To get account ID:")
    print("  1. Go to https://developers.facebook.com/tools/explorer/")
    print("  2. Use your Instagram access token")
    print("  3. Query: GET /me?fields=id")
    print("  4. Or use: GET /{username}?fields=id")
    print()
    
    test_source = Source(
        platform="Instagram",
        account_handle="bbcnews",  # Replace with actual account ID
        account_name="BBC News",
        account_id=None  # Set this to actual Instagram account ID
    )
    
    scraper = InstagramScraper()
    
    print(f"Testing Instagram scraper with account: {test_source.account_handle}")
    print("This may take a moment...\n")
    
    try:
        posts = scraper.fetch_posts(test_source, limit=5)
        
        if len(posts) == 0:
            print("⚠ No posts fetched")
            print("\nPossible reasons:")
            print("  - Account ID is incorrect (need numeric ID, not handle)")
            print("  - Access token doesn't have 'instagram_basic' permission")
            print("  - Account doesn't exist or is private")
            return False
        
        print(f"✓ Successfully fetched {len(posts)} posts!\n")
        
        # Show first post
        if posts:
            post = posts[0]
            print("Sample post:")
            print(f"  ID: {post['platform_post_id']}")
            print(f"  Content: {post['content'][:60]}...")
            print(f"  Likes: {post['likes']}, Comments: {post['comments']}")
            print(f"  URL: {post['url']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Instagram test error: {e}")
        return False


def main():
    """Run tests."""
    print("\n" + "=" * 60)
    print("FACEBOOK & INSTAGRAM SCRAPER TEST")
    print("=" * 60)
    print()
    
    # Test database
    if not test_connection():
        print("✗ Database connection failed")
        return 1
    
    print("✓ Database connected\n")
    
    # Test Facebook
    fb_success = test_facebook()
    
    # Test Instagram
    ig_success = test_instagram()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    
    if fb_success:
        print("✓ Facebook scraper is working!")
    else:
        print("✗ Facebook scraper needs configuration")
        print("  - Get page ID from Facebook Graph API Explorer")
        print("  - Update source.account_id in database")
    
    if ig_success:
        print("✓ Instagram scraper is working!")
    else:
        print("✗ Instagram scraper needs configuration")
        print("  - Get account ID from Facebook Graph API Explorer")
        print("  - Update source.account_id in database")
    
    print("\nNext steps:")
    print("  1. Get page/account IDs from Graph API Explorer")
    print("  2. Update sources in database with correct IDs")
    print("  3. Run 'python trigger_scrape.py' to fetch data")
    print("  4. Check dashboard for stories")
    
    return 0 if (fb_success and ig_success) else 1


if __name__ == "__main__":
    sys.exit(main())
