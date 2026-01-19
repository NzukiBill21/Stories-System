"""Activate Instagram source."""
from database import SessionLocal
from models import Source

db = SessionLocal()
try:
    instagram = db.query(Source).filter(Source.platform == 'Instagram').first()
    if instagram:
        instagram.is_active = True
        db.commit()
        print(f"Instagram source activated: {instagram.account_name}")
    else:
        print("No Instagram source found")
finally:
    db.close()
