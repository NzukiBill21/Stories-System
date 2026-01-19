"""Update BBC News scrape frequency to 10 minutes."""
from database import SessionLocal
from models import Source

db = SessionLocal()
try:
    source = db.query(Source).filter(Source.account_name == 'BBC News').first()
    if source:
        print(f"Found: {source.account_name}")
        print(f"Current frequency: {source.scrape_frequency_minutes} minutes")
        source.scrape_frequency_minutes = 10  # Every 10 minutes
        db.commit()
        print(f"Updated frequency: {source.scrape_frequency_minutes} minutes")
        print("[SUCCESS] BBC News will now scrape every 10 minutes")
    else:
        print("❌ BBC News source not found")
finally:
    db.close()
