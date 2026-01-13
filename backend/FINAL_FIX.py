"""Final comprehensive fix - updates .env and fixes everything."""
import os
import re
import pymysql
from database import SessionLocal, Base, engine
from models import Source, RawPost, Story
from config import settings

def update_env_password():
    """Update .env to have empty password."""
    env_path = ".env"
    if not os.path.exists(env_path):
        print("[ERROR] .env file not found")
        return False
    
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace DB_PASSWORD line
    new_content = re.sub(
        r'DB_PASSWORD=.*',
        'DB_PASSWORD=',
        content,
        flags=re.MULTILINE
    )
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[OK] Updated .env: DB_PASSWORD=")
    return True

def configure_sources_direct():
    """Configure sources using direct MySQL connection."""
    print("\nConfiguring sources via direct MySQL...")
    
    conn = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password="",
        database=settings.db_name
    )
    
    cursor = conn.cursor()
    
    try:
        # Disable Twitter/Instagram
        cursor.execute("UPDATE sources SET is_active = 0 WHERE platform IN ('X', 'Twitter', 'Instagram')")
        print(f"[OK] Disabled Twitter/Instagram: {cursor.rowcount} sources")
        
        # Enable/Update Facebook
        cursor.execute("""
            INSERT INTO sources (platform, account_handle, account_name, account_id, is_active, created_at, updated_at)
            VALUES ('Facebook', 'Bee Bill', 'Bee Bill', '1412325813805867', 1, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                account_id = '1412325813805867',
                account_handle = 'Bee Bill',
                account_name = 'Bee Bill',
                is_active = 1,
                updated_at = NOW()
        """)
        print("[OK] Configured Facebook source")
        
        # Enable TikTok
        cursor.execute("UPDATE sources SET is_active = 1 WHERE platform = 'TikTok'")
        print(f"[OK] Enabled TikTok: {cursor.rowcount} sources")
        
        conn.commit()
        
        # Show summary
        cursor.execute("SELECT platform, account_handle, account_id FROM sources WHERE is_active = 1")
        active = cursor.fetchall()
        print(f"\nActive sources: {len(active)}")
        for row in active:
            print(f"  - {row[0]}: {row[1]} (ID: {row[2]})")
        
        # Show data counts
        cursor.execute("SELECT COUNT(*) FROM raw_posts")
        posts = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM stories")
        stories = cursor.fetchone()[0]
        print(f"\nRaw posts: {posts}")
        print(f"Stories: {stories}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Final fix."""
    print("=" * 60)
    print("FINAL COMPREHENSIVE FIX")
    print("=" * 60)
    print()
    
    # Step 1: Update .env
    if not update_env_password():
        return 1
    
    # Step 2: Test direct connection
    print("\nTesting MySQL connection...")
    try:
        conn = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password="",
            database=settings.db_name
        )
        print("[OK] MySQL connection works!")
        conn.close()
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1
    
    # Step 3: Configure sources
    if not configure_sources_direct():
        return 1
    
    print("\n" + "=" * 60)
    print("ALL FIXED!")
    print("=" * 60)
    print("\nIMPORTANT: Restart Python to reload .env changes")
    print("Then run: python trigger_scrape_now.py")
    print("\nOr test scraping now:")
    print("  python -c \"from database import SessionLocal; from models import Source; db = SessionLocal(); print('Sources:', db.query(Source).filter(Source.is_active==True).count())\"")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
