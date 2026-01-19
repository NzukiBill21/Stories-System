"""Fix sources with None scrape_frequency_minutes."""
from database import SessionLocal
from models import Source

db = SessionLocal()
try:
    # Find sources with None frequency
    sources = db.query(Source).filter(Source.scrape_frequency_minutes == None).all()
    
    if not sources:
        print("No sources with None frequency found")
    else:
        print(f"Found {len(sources)} sources with None frequency")
        
        # Set default frequency to 30 minutes
        for source in sources:
            source.scrape_frequency_minutes = 30
            print(f"  - Updated {source.account_name} ({source.platform}): 30 minutes")
        
        db.commit()
        print(f"\n[SUCCESS] Updated {len(sources)} sources to 30 minutes default frequency")
        
finally:
    db.close()
