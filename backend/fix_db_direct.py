"""Direct database fix - bypasses SQLAlchemy to test connection."""
import pymysql
from database import SessionLocal, Base
from models import Source, RawPost, Story, Hashtag, ScrapeLog
from config import settings

def main():
    """Fix database and configure everything."""
    print("=" * 60)
    print("DIRECT DATABASE FIX")
    print("=" * 60)
    print()
    
    # Test direct connection
    print("Testing direct MySQL connection...")
    try:
        conn = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password="",  # Empty password
            database=settings.db_name,
            connect_timeout=5
        )
        print("[OK] Direct connection works!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"[OK] MySQL version: {version[0]}")
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"[OK] Found {len(tables)} table(s)")
        
        conn.close()
        
        # Now configure sources using SQLAlchemy but with workaround
        print("\nConfiguring sources...")
        db = SessionLocal()
        
        try:
            # Disable Twitter/Instagram
            for platform in ["X", "Twitter", "Instagram"]:
                sources = db.query(Source).filter(Source.platform == platform).all()
                for s in sources:
                    s.is_active = False
                    print(f"[OK] Disabled: {s.platform}")
            
            # Enable/Create Facebook
            fb = db.query(Source).filter(Source.platform == "Facebook").first()
            if fb:
                fb.is_active = True
                fb.account_id = "1412325813805867"
                fb.account_handle = "Bee Bill"
                fb.account_name = "Bee Bill"
                print(f"[OK] Enabled: Facebook - Bee Bill")
            else:
                fb = Source(
                    platform="Facebook",
                    account_handle="Bee Bill",
                    account_name="Bee Bill",
                    account_id="1412325813805867",
                    is_active=True
                )
                db.add(fb)
                print(f"[OK] Created: Facebook - Bee Bill")
            
            # Enable TikTok
            tiktok = db.query(Source).filter(Source.platform == "TikTok").all()
            for s in tiktok:
                s.is_active = True
                print(f"[OK] Enabled: {s.platform}")
            
            db.commit()
            
            # Show data
            print("\n" + "=" * 60)
            print("DATA SUMMARY")
            print("=" * 60)
            
            active = db.query(Source).filter(Source.is_active == True).all()
            print(f"\nActive sources: {len(active)}")
            for s in active:
                print(f"  - {s.platform}: {s.account_handle} (ID: {s.account_id})")
            
            posts = db.query(RawPost).count()
            stories = db.query(Story).count()
            print(f"\nRaw posts: {posts}")
            print(f"Stories: {stories}")
            
            if stories > 0:
                recent = db.query(Story).order_by(Story.created_at.desc()).limit(5).all()
                print("\nRecent stories:")
                for story in recent:
                    print(f"  - {story.platform}: {story.title[:50]}... (Score: {story.score:.1f})")
            
            print("\n" + "=" * 60)
            print("ALL FIXED!")
            print("=" * 60)
            print("\nNext: Update .env with: DB_PASSWORD=")
            print("Then run: python trigger_scrape_now.py")
            
            return 0
            
        except Exception as e:
            print(f"[ERROR] {e}")
            db.rollback()
            return 1
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\nUpdate .env: DB_PASSWORD=")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
