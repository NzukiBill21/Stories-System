"""Setup sources for trending content discovery - TikTok and trending Facebook posts."""
from database import SessionLocal, test_connection
from models import Source
from loguru import logger
import sys

def main():
    """Setup sources for trending content."""
    print("=" * 60)
    print("Setup Trending Content Sources")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    print("[OK] Database connected\n")
    
    db = SessionLocal()
    try:
        # Create TikTok source for trending videos
        tiktok = db.query(Source).filter(Source.platform == "TikTok").first()
        if not tiktok:
            tiktok = Source(
                platform="TikTok",
                account_handle="trending",
                account_name="TikTok Trending",
                account_id=None,  # TikTok doesn't need account ID for trending
                is_active=True,
                is_trusted=False,
                scrape_frequency_minutes=30
            )
            db.add(tiktok)
            print("[OK] Created TikTok trending source")
        else:
            tiktok.is_active = True
            tiktok.account_handle = "trending"
            tiktok.account_name = "TikTok Trending"
            print("[OK] Updated TikTok trending source")
        
        # Update Facebook source (user profile)
        facebook = db.query(Source).filter(Source.platform == "Facebook").first()
        if facebook:
            facebook.is_active = True
            facebook.account_id = "1412325813805867"
            facebook.account_handle = "Bee Bill"
            facebook.account_name = "Bee Bill"
            print("[OK] Updated Facebook source (user profile)")
        else:
            facebook = Source(
                platform="Facebook",
                account_handle="Bee Bill",
                account_name="Bee Bill",
                account_id="1412325813805867",
                is_active=True
            )
            db.add(facebook)
            print("[OK] Created Facebook source")
        
        # Disable Twitter/Instagram
        for platform in ["X", "Twitter", "Instagram"]:
            sources = db.query(Source).filter(Source.platform == platform).all()
            for s in sources:
                s.is_active = False
                print(f"[OK] Disabled: {s.platform}")
        
        db.commit()
        
        # Show active sources
        active = db.query(Source).filter(Source.is_active == True).all()
        print("\n" + "=" * 60)
        print("ACTIVE SOURCES FOR TRENDING CONTENT")
        print("=" * 60)
        print()
        for s in active:
            print(f"  [OK] {s.platform}: {s.account_name}")
            print(f"     Handle: {s.account_handle}")
            if s.account_id:
                print(f"     ID: {s.account_id}")
            print()
        
        print("=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        print("\nSources configured for trending content:")
        print("  - TikTok: Fetches trending videos (high engagement)")
        print("  - Facebook: Fetches posts from user profile")
        print("\nNext: Run 'python trigger_scrape_now.py' to start scraping!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
