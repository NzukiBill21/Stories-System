"""Disable Instagram source temporarily."""
from database import SessionLocal, test_connection
from models import Source

def main():
    """Disable Instagram source."""
    print("=" * 60)
    print("Disable Instagram Source")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    print("[OK] Database connected\n")
    
    db = SessionLocal()
    try:
        ig_sources = db.query(Source).filter(Source.platform == "Instagram").all()
        
        if not ig_sources:
            print("[INFO] No Instagram sources found")
            return 0
        
        for source in ig_sources:
            source.is_active = False
            print(f"[OK] Disabled: {source.account_handle or source.account_name}")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("[OK] Instagram sources disabled")
        print("=" * 60)
        print("\nYour system will now focus on:")
        print("  - Facebook (working!)")
        print("  - Twitter/X (add token)")
        print("  - TikTok (configured)")
        print("\nInstagram can be added later when app is configured.")
        print("\nTo re-enable later:")
        print("  source.is_active = True")
        
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
