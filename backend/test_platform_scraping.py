"""Test scraping for TikTok, X, Facebook, Instagram."""
from database import SessionLocal
from models import Source
from services import scrape_source
from loguru import logger
import sys

def test_platform_scraping():
    """Test scraping for each platform."""
    db = SessionLocal()
    try:
        platforms = ['TikTok', 'X', 'Facebook', 'Instagram']
        
        print("=" * 60)
        print("Testing Platform Scraping")
        print("=" * 60)
        print()
        
        for platform in platforms:
            print(f"\n{platform}:")
            print("-" * 40)
            
            sources = db.query(Source).filter(
                Source.platform == platform,
                Source.is_active == True
            ).limit(1).all()
            
            if not sources:
                print(f"  No active sources found")
                continue
            
            source = sources[0]
            print(f"  Source: {source.account_name}")
            print(f"  Handle: {source.account_handle}")
            print(f"  Testing scrape...")
            
            try:
                result = scrape_source(db, source.id)
                print(f"  Result:")
                print(f"    Posts fetched: {result.get('posts_fetched', 0)}")
                print(f"    Stories created: {result.get('stories_created', 0)}")
                
                if 'error' in result:
                    print(f"    ERROR: {result['error']}")
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("Testing Complete")
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    test_platform_scraping()
