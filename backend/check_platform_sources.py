"""Check sources for TikTok, X, Facebook, Instagram."""
from database import SessionLocal
from models import Source

db = SessionLocal()
try:
    platforms = ['TikTok', 'X', 'Facebook', 'Instagram']
    
    print("=" * 60)
    print("Platform Sources Status")
    print("=" * 60)
    print()
    
    for platform in platforms:
        sources = db.query(Source).filter(
            Source.platform == platform
        ).all()
        
        active_sources = [s for s in sources if s.is_active]
        
        print(f"{platform}:")
        print(f"  Total sources: {len(sources)}")
        print(f"  Active sources: {len(active_sources)}")
        
        if active_sources:
            for s in active_sources[:5]:
                print(f"    - {s.account_name}")
                print(f"      Handle: {s.account_handle}")
                print(f"      Frequency: {s.scrape_frequency_minutes} min")
                print(f"      Last checked: {s.last_checked_at}")
                print(f"      Account ID: {s.account_id}")
        else:
            print("    No active sources!")
        
        print()
    
finally:
    db.close()
