"""Verification script to ensure data is flowing correctly through the system."""
from database import SessionLocal, test_connection
from models import Source, RawPost, Story, ScrapeLog
from services import scrape_source, get_trending_stories
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from loguru import logger
import sys


def check_database_connection():
    """Check if database connection works."""
    print("=" * 60)
    print("1. DATABASE CONNECTION")
    print("=" * 60)
    if test_connection():
        print("✓ Database connected successfully\n")
        return True
    else:
        print("✗ Database connection failed\n")
        return False


def check_tables_exist():
    """Check if all required tables exist."""
    print("=" * 60)
    print("2. DATABASE TABLES")
    print("=" * 60)
    db = SessionLocal()
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        required_tables = ['sources', 'raw_posts', 'stories', 'scrape_logs']
        all_exist = True
        
        for table in required_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' NOT FOUND")
                all_exist = False
        
        print()
        return all_exist
    except Exception as e:
        print(f"✗ Error checking tables: {e}\n")
        return False
    finally:
        db.close()


def check_sources():
    """Check if sources are configured."""
    print("=" * 60)
    print("3. SOURCES CONFIGURATION")
    print("=" * 60)
    db = SessionLocal()
    try:
        sources = db.query(Source).all()
        active_sources = db.query(Source).filter(Source.is_active == True).all()
        
        print(f"Total sources: {len(sources)}")
        print(f"Active sources: {len(active_sources)}")
        
        if len(active_sources) == 0:
            print("⚠ WARNING: No active sources configured!")
            print("  Run 'python init_db.py' to add sample sources")
            print()
            return False
        
        print("\nActive sources:")
        for source in active_sources:
            print(f"  - {source.platform}: {source.account_handle} ({source.account_name})")
            print(f"    Frequency: {source.scrape_frequency_minutes} minutes")
            print(f"    Trusted: {'Yes' if source.is_trusted else 'No'}")
            if source.last_checked_at:
                print(f"    Last checked: {source.last_checked_at}")
            else:
                print(f"    Last checked: Never")
            print()
        
        return True
    except Exception as e:
        print(f"✗ Error checking sources: {e}\n")
        return False
    finally:
        db.close()


def check_data():
    """Check if data exists in database."""
    print("=" * 60)
    print("4. DATA IN DATABASE")
    print("=" * 60)
    db = SessionLocal()
    try:
        raw_posts_count = db.query(RawPost).count()
        stories_count = db.query(Story).count()
        active_stories_count = db.query(Story).filter(Story.is_active == True).count()
        
        print(f"Raw posts: {raw_posts_count}")
        print(f"Total stories: {stories_count}")
        print(f"Active stories: {active_stories_count}")
        
        if stories_count == 0:
            print("\n⚠ WARNING: No stories found in database!")
            print("  You need to trigger scraping to collect data.")
            print("  See step 5 below.\n")
            return False
        
        # Check story hierarchy (sorted by score)
        top_stories = db.query(Story).filter(Story.is_active == True).order_by(desc(Story.score)).limit(5).all()
        
        print(f"\nTop 5 stories (by score):")
        for i, story in enumerate(top_stories, 1):
            print(f"  {i}. Score: {story.score:.1f} | {story.platform} | {story.headline[:50]}...")
            print(f"     Engagement: {story.likes + story.comments + story.shares} | Velocity: {story.engagement_velocity:.1f}/hr")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Error checking data: {e}\n")
        return False
    finally:
        db.close()


def check_scrape_logs():
    """Check recent scraping activity."""
    print("=" * 60)
    print("5. SCRAPING ACTIVITY")
    print("=" * 60)
    db = SessionLocal()
    try:
        recent_logs = db.query(ScrapeLog).order_by(desc(ScrapeLog.started_at)).limit(10).all()
        
        if len(recent_logs) == 0:
            print("⚠ No scraping activity found")
            print("  Scraping hasn't been triggered yet.\n")
            return False
        
        print(f"Recent scraping activity (last 10):\n")
        for log in recent_logs:
            source = db.query(Source).filter(Source.id == log.source_id).first()
            source_name = source.account_handle if source else f"Source {log.source_id}"
            
            status_icon = "✓" if log.status == "success" else "✗" if log.status == "error" else "⏳"
            print(f"{status_icon} {source_name} | {log.status.upper()}")
            print(f"  Started: {log.started_at}")
            if log.completed_at:
                print(f"  Duration: {log.duration_seconds:.1f}s")
            print(f"  Posts fetched: {log.posts_fetched} | Processed: {log.posts_processed} | Stories: {log.stories_created}")
            if log.error_message:
                print(f"  Error: {log.error_message[:100]}")
            print()
        
        return True
    except Exception as e:
        print(f"✗ Error checking scrape logs: {e}\n")
        return False
    finally:
        db.close()


def trigger_test_scrape():
    """Offer to trigger a test scrape."""
    print("=" * 60)
    print("6. TRIGGER TEST SCRAPE")
    print("=" * 60)
    db = SessionLocal()
    try:
        active_sources = db.query(Source).filter(Source.is_active == True).limit(1).all()
        
        if len(active_sources) == 0:
            print("⚠ No active sources to scrape")
            print("  Run 'python init_db.py' first\n")
            return False
        
        source = active_sources[0]
        print(f"Triggering scrape for: {source.account_handle} ({source.platform})")
        print("This may take a moment...\n")
        
        result = scrape_source(db, source.id)
        
        if "error" in result:
            print(f"✗ Scrape failed: {result['error']}\n")
            return False
        
        print(f"✓ Scrape completed successfully!")
        print(f"  Posts fetched: {result['posts_fetched']}")
        print(f"  Posts processed: {result['posts_processed']}")
        print(f"  Stories created: {result['stories_created']}\n")
        
        return True
    except Exception as e:
        print(f"✗ Error during test scrape: {e}\n")
        return False
    finally:
        db.close()


def check_api_endpoint():
    """Check if API endpoint returns data correctly."""
    print("=" * 60)
    print("7. API ENDPOINT VERIFICATION")
    print("=" * 60)
    try:
        import requests
        response = requests.get("http://localhost:8000/api/stories?limit=5", timeout=5)
        
        if response.status_code == 200:
            stories = response.json()
            print(f"✓ API endpoint working")
            print(f"  Returned {len(stories)} stories")
            
            if len(stories) > 0:
                print("\n  Stories returned (should be sorted by score, highest first):")
                for i, story in enumerate(stories, 1):
                    print(f"    {i}. Score: {story.get('credibility', 'N/A')} | {story.get('platform')} | {story.get('headline', '')[:40]}...")
            
            print()
            return True
        else:
            print(f"✗ API returned status {response.status_code}\n")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠ API server not running")
        print("  Start it with: python main.py\n")
        return False
    except Exception as e:
        print(f"✗ Error checking API: {e}\n")
        return False


def verify_story_hierarchy():
    """Verify stories are properly sorted by score."""
    print("=" * 60)
    print("8. STORY HIERARCHY VERIFICATION")
    print("=" * 60)
    db = SessionLocal()
    try:
        # Get stories as API would return them
        stories = get_trending_stories(db, limit=10, hours_back=168)
        
        if len(stories) == 0:
            print("⚠ No stories to verify hierarchy\n")
            return False
        
        print("Stories sorted by score (highest to lowest):\n")
        scores = []
        for i, story in enumerate(stories, 1):
            scores.append(story.score)
            print(f"{i}. Score: {story.score:.2f} | Velocity: {story.engagement_velocity:.1f}/hr | {story.platform}")
            print(f"   {story.headline[:60]}...")
            print(f"   Engagement: {story.likes + story.comments + story.shares} | Credibility: {story.credibility_score:.0f}%")
            print()
        
        # Verify sorting
        is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
        if is_sorted:
            print("✓ Stories are correctly sorted by score (highest first)\n")
        else:
            print("✗ WARNING: Stories are NOT properly sorted!\n")
        
        return is_sorted
    except Exception as e:
        print(f"✗ Error verifying hierarchy: {e}\n")
        return False
    finally:
        db.close()


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("STORY INTELLIGENCE DASHBOARD - DATA FLOW VERIFICATION")
    print("=" * 60 + "\n")
    
    checks = [
        ("Database Connection", check_database_connection),
        ("Database Tables", check_tables_exist),
        ("Sources Configuration", check_sources),
        ("Data in Database", check_data),
        ("Scraping Activity", check_scrape_logs),
        ("Story Hierarchy", verify_story_hierarchy),
        ("API Endpoint", check_api_endpoint),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Error in {name}: {e}\n")
            results[name] = False
    
    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✓ All checks passed! System is ready.")
        print("\nNext steps:")
        print("  1. Ensure Celery worker and beat are running for automatic scraping")
        print("  2. Start the API server: python main.py")
        print("  3. Start the frontend: npm run dev")
        print("  4. Open http://localhost:5173 to view the dashboard")
    else:
        print("⚠ Some checks failed. Please address the issues above.")
        print("\nCommon fixes:")
        print("  - Run 'python init_db.py' to create tables and add sources")
        print("  - Trigger manual scrape: python trigger_scrape.py")
        print("  - Check API keys in .env file")
        print("  - Ensure MySQL database is running and accessible")
    
    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
