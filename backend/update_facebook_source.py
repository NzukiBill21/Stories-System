"""Quick script to update Facebook source with your page ID."""
from database import SessionLocal, test_connection
from models import Source

def main():
    """Update Facebook source with page ID."""
    print("=" * 60)
    print("Update Facebook Source")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    print("[OK] Database connected\n")
    
    db = SessionLocal()
    try:
        # Your page info
        page_id = "1412325813805867"
        page_name = "Bee Bill"
        
        # Find existing Facebook source
        source = db.query(Source).filter(Source.platform == "Facebook").first()
        
        if source:
            source.account_id = page_id
            source.account_handle = page_name
            source.account_name = page_name
            source.is_active = True
            print(f"[OK] Updated Facebook source:")
            print(f"     Platform: {source.platform}")
            print(f"     Name: {source.account_name}")
            print(f"     ID: {source.account_id}")
        else:
            source = Source(
                platform="Facebook",
                account_handle=page_name,
                account_name=page_name,
                account_id=page_id,
                is_active=True
            )
            db.add(source)
            print(f"[OK] Created Facebook source:")
            print(f"     Platform: {source.platform}")
            print(f"     Name: {source.account_name}")
            print(f"     ID: {source.account_id}")
        
        db.commit()
        print("\n[OK] Database updated successfully!")
        print("\nNext step: Get a new Facebook token and update .env file")
        print("See: backend/FACEBOOK_TOKEN_FIX.md")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    sys.exit(main())
