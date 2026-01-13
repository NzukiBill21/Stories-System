"""Manual script to trigger scraping for all active sources."""
from database import SessionLocal, test_connection
from models import Source
from services import scrape_source
from loguru import logger
import sys


def main():
    """Trigger scraping for all active sources."""
    print("=" * 60)
    print("MANUAL SCRAPE TRIGGER")
    print("=" * 60)
    print()
    
    # Test connection
    if not test_connection():
        print("✗ Database connection failed. Please check your configuration.")
        return 1
    
    print("✓ Database connected\n")
    
    db = SessionLocal()
    try:
        # Get all active sources
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        if len(sources) == 0:
            print("⚠ No active sources found.")
            print("  Run 'python init_db.py' to add sources first.")
            return 1
        
        print(f"Found {len(sources)} active source(s):\n")
        for source in sources:
            print(f"  - {source.platform}: {source.account_handle}")
        print()
        
        # Ask for confirmation
        response = input("Trigger scraping for all sources? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return 0
        
        print("\nStarting scraping...\n")
        
        # Scrape each source
        results = []
        for source in sources:
            print(f"Scraping {source.account_handle} ({source.platform})...")
            try:
                result = scrape_source(db, source.id)
                results.append({
                    'source': source.account_handle,
                    'platform': source.platform,
                    'result': result
                })
                
                if "error" in result:
                    print(f"  ✗ Error: {result['error']}")
                else:
                    print(f"  ✓ Posts fetched: {result['posts_fetched']}")
                    print(f"  ✓ Posts processed: {result['posts_processed']}")
                    print(f"  ✓ Stories created: {result['stories_created']}")
                print()
            except Exception as e:
                print(f"  ✗ Exception: {e}\n")
                results.append({
                    'source': source.account_handle,
                    'platform': source.platform,
                    'result': {'error': str(e)}
                })
        
        # Summary
        print("=" * 60)
        print("SCRAPING SUMMARY")
        print("=" * 60)
        
        total_posts = sum(r['result'].get('posts_fetched', 0) for r in results)
        total_stories = sum(r['result'].get('stories_created', 0) for r in results)
        
        print(f"Total posts fetched: {total_posts}")
        print(f"Total stories created: {total_stories}")
        print()
        
        if total_stories > 0:
            print("✓ Scraping completed! Stories are now available in the dashboard.")
            print("  Run 'python verify_data_flow.py' to verify everything is working.")
        else:
            print("⚠ No stories were created. This could mean:")
            print("  - No new posts found")
            print("  - Posts didn't meet scoring thresholds")
            print("  - API keys may be missing or invalid")
            print("  - Check scrape logs for details")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"✗ Error: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
