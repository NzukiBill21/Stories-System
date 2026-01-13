"""
Scrape Facebook Trends - Aggregates from multiple Pages and computes trends.

This script implements the proper Facebook trends strategy:
1. Fetch from multiple public Facebook Pages (not user profiles)
2. Compute trend_score = (likes + comments + shares) / minutes_since_posted
3. Rank by trend_score DESC
4. Store top N trending posts
"""
from database import SessionLocal, test_connection
from models import Source
from trend_aggregator import scrape_and_store_trends
from loguru import logger
import sys


def main():
    """Main function to scrape Facebook trends."""
    print("=" * 60)
    print("Facebook Trends Aggregator")
    print("=" * 60)
    print()
    print("Strategy:")
    print("  - Aggregate posts from multiple Facebook Pages")
    print("  - Compute trend_score = (likes + comments + shares) / minutes_since_posted")
    print("  - Rank by trend_score DESC")
    print("  - Store top trending posts")
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    db = SessionLocal()
    try:
        # Get all active Facebook Pages (not user profiles)
        facebook_pages = db.query(Source).filter(
            Source.platform == "Facebook",
            Source.is_active == True,
            Source.account_id.isnot(None)  # Must have Page ID
        ).all()
        
        if not facebook_pages:
            print("[WARNING] No active Facebook Pages found!")
            print()
            print("To add Facebook Pages:")
            print("  1. Find public Facebook Pages (e.g., BBC News, CNN, Citizen TV Kenya)")
            print("  2. Get Page ID from Graph API Explorer")
            print("  3. Add to database using add_facebook_pages.py")
            print()
            return 1
        
        print(f"Found {len(facebook_pages)} active Facebook Page(s):")
        for page in facebook_pages:
            print(f"  - {page.account_name or page.account_handle} (ID: {page.account_id})")
        print()
        
        # Scrape and aggregate trends
        print("Aggregating trends from Facebook Pages...")
        result = scrape_and_store_trends(
            db=db,
            page_sources=facebook_pages,
            posts_per_page=10,  # Fetch 10 posts per page
            top_n=50,  # Keep top 50 trending posts
            min_trend_score=10.0  # Minimum 10 engagement per minute
        )
        
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Pages scraped: {result.get('pages_scraped', 0)}")
        print(f"Posts fetched: {result.get('posts_fetched', 0)}")
        print(f"Posts stored: {result.get('posts_stored', 0)}")
        print(f"Top trending: {result.get('top_trending', 0)}")
        print()
        
        if result.get('posts_stored', 0) > 0:
            print("[OK] Trending posts stored in database!")
            print()
            print("Next steps:")
            print("  1. Process posts to stories: python process_posts_to_stories.py")
            print("  2. Or wait for automatic processing")
            print("  3. View dashboard to see trending stories")
        else:
            print("[INFO] No new trending posts found")
            print("This could mean:")
            print("  - Pages have no recent posts")
            print("  - Posts don't meet trend_score threshold")
            print("  - Need to add more Facebook Pages")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
