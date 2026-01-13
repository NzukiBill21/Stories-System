"""Disable Twitter and Instagram, focus on Facebook and TikTok."""
from database import SessionLocal, test_connection
from models import Source
from loguru import logger

def main():
    """Disable Twitter and Instagram sources, keep Facebook and TikTok active."""
    print("=" * 60)
    print("Focus on Facebook & TikTok")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        print("Please check your database credentials in .env")
        return 1
    
    print("[OK] Database connected\n")
    
    db = SessionLocal()
    try:
        # Disable Twitter/X
        twitter_sources = db.query(Source).filter(Source.platform.in_(["X", "Twitter"])).all()
        for source in twitter_sources:
            source.is_active = False
            print(f"[OK] Disabled: {source.platform} - {source.account_handle}")
        
        # Disable Instagram
        instagram_sources = db.query(Source).filter(Source.platform == "Instagram").all()
        for source in instagram_sources:
            source.is_active = False
            print(f"[OK] Disabled: {source.platform} - {source.account_handle}")
        
        # Keep Facebook active
        facebook_sources = db.query(Source).filter(Source.platform == "Facebook").all()
        for source in facebook_sources:
            source.is_active = True
            print(f"[OK] Enabled: {source.platform} - {source.account_handle} (ID: {source.account_id})")
        
        # Keep TikTok active
        tiktok_sources = db.query(Source).filter(Source.platform == "TikTok").all()
        for source in tiktok_sources:
            source.is_active = True
            print(f"[OK] Enabled: {source.platform} - {source.account_handle}")
        
        db.commit()
        
        # Summary
        active_sources = db.query(Source).filter(Source.is_active == True).all()
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"\nActive sources: {len(active_sources)}")
        for source in active_sources:
            print(f"  - {source.platform}: {source.account_handle}")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("\n1. Test Facebook scraping:")
        print("   python test_facebook_instagram.py")
        print("\n2. Test TikTok scraping:")
        print("   python test_tiktok_scraper.py")
        print("\n3. Trigger scraping:")
        print("   python trigger_scrape.py")
        print("\n4. Start services:")
        print("   python main.py  # API")
        print("   celery -A celery_app worker --loglevel=info  # Worker")
        print("   celery -A celery_app beat --loglevel=info  # Scheduler")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    sys.exit(main())
