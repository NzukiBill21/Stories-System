"""Test script for TikTok scraper."""
from platforms.tiktok import TikTokScraper
from models import Source
from database import SessionLocal, test_connection
from loguru import logger
import sys


def main():
    """Test TikTok scraper functionality."""
    print("=" * 60)
    print("TikTok Scraper Test")
    print("=" * 60)
    print()
    
    # Test database connection
    if not test_connection():
        print("✗ Database connection failed")
        return 1
    
    print("✓ Database connected\n")
    
    # Create test source
    test_source = Source(
        platform="TikTok",
        account_handle="trending",
        account_name="TikTok Trending",
        is_active=True
    )
    
    # Initialize scraper
    print("Initializing TikTok scraper...")
    try:
        scraper = TikTokScraper()
        print("✓ Scraper initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize scraper: {e}")
        print("\nMake sure you've installed:")
        print("  pip install TikTokApi playwright")
        print("  playwright install chromium")
        return 1
    
    # Test fetching videos
    print("Fetching trending videos (limit: 5)...")
    print("This may take 30-60 seconds...\n")
    
    try:
        videos = scraper.fetch_posts(test_source, limit=5)
        
        if len(videos) == 0:
            print("⚠ No videos fetched")
            print("\nPossible reasons:")
            print("  - TikTokApi not working")
            print("  - Network issues")
            print("  - All videos filtered out (check TIKTOK_MIN_ENGAGEMENT_VELOCITY)")
            return 1
        
        print(f"✓ Fetched {len(videos)} videos\n")
        
        # Display results
        print("=" * 60)
        print("Fetched Videos")
        print("=" * 60)
        print()
        
        for i, video in enumerate(videos, 1):
            print(f"{i}. Video ID: {video['platform_post_id']}")
            print(f"   Author: {video['author']}")
            print(f"   Caption: {video['content'][:60]}...")
            print(f"   Engagement: {video['likes']} likes, {video['comments']} comments, {video['shares']} shares")
            print(f"   Views: {video['views']}")
            print(f"   Posted: {video['posted_at']}")
            print(f"   URL: {video['url']}")
            
            # Calculate velocity for display
            from datetime import datetime
            posted_at = video['posted_at']
            if isinstance(posted_at, datetime):
                time_diff = datetime.utcnow() - posted_at
                minutes = max(time_diff.total_seconds() / 60, 0.1)
                total_engagement = video['likes'] + video['comments'] + video['shares']
                velocity = total_engagement / minutes
                print(f"   Velocity: {velocity:.2f} engagement/minute")
            print()
        
        print("=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        print(f"\n✓ Scraper is working correctly")
        print(f"✓ Fetched {len(videos)} high-engagement videos")
        print("\nNext steps:")
        print("  1. Add TikTok source to database")
        print("  2. Run 'python trigger_scrape.py' to scrape")
        print("  3. Check dashboard for TikTok stories")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check TikTokApi is installed: pip install TikTokApi")
        print("  2. Check Playwright is installed: playwright install chromium")
        print("  3. Check internet connection")
        print("  4. Check TikTokApi library version compatibility")
        return 1


if __name__ == "__main__":
    sys.exit(main())
