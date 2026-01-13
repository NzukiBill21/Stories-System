"""Test that API returns data correctly."""
from database import SessionLocal
from models import Story, Source
from api import story_to_response

def main():
    """Test API data."""
    print("=" * 60)
    print("Testing API Data")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Check stories
        stories = db.query(Story).filter(Story.is_active == True).limit(5).all()
        print(f"Stories in database: {len(stories)}")
        
        if stories:
            print("\nSample stories:")
            for story in stories:
                resp = story_to_response(story)
                print(f"\n  {story.platform}:")
                print(f"    Headline: {resp.headline[:60]}...")
                print(f"    Source: {resp.source}")
                print(f"    Platform: {resp.platform}")
                print(f"    Engagement: {resp.engagement}")
                print(f"    Velocity: {resp.velocity}")
                print(f"    Score: {story.score:.1f}")
        else:
            print("\n[WARNING] No stories found")
            print("Run: python create_test_data.py")
        
        # Check sources
        sources = db.query(Source).filter(Source.is_active == True).all()
        print(f"\n\nSources in database: {len(sources)}")
        for source in sources:
            print(f"  - {source.platform}: {source.account_name or source.account_handle}")
        
        print("\n" + "=" * 60)
        if stories:
            print("[OK] Data is ready for dashboard!")
            print("Start API: python main.py")
            print("View dashboard: http://localhost:3000")
        else:
            print("[INFO] No stories - create test data or scrape real data")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    sys.exit(main())
