"""Update database schema to include new Kenyan content fields."""
from database import engine, Base, test_connection
from models import Source, RawPost, Story, Hashtag, ScrapeLog
from sqlalchemy import text
from loguru import logger
import sys


def update_schema():
    """Update database schema with new fields."""
    print("=" * 60)
    print("Database Schema Update")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return False
    
    print("[OK] Database connected\n")
    
    try:
        with engine.connect() as conn:
            # Check if new columns exist
            result = conn.execute(text("SHOW COLUMNS FROM sources LIKE 'is_kenyan'"))
            has_kenyan = result.fetchone() is not None
            
            if not has_kenyan:
                print("Updating sources table...")
                # Add new columns to sources
                conn.execute(text("ALTER TABLE sources ADD COLUMN is_kenyan BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE sources ADD COLUMN location VARCHAR(255)"))
                conn.execute(text("CREATE INDEX idx_source_kenyan ON sources(is_kenyan)"))
                print("[OK] Added is_kenyan and location to sources table")
            else:
                print("[OK] sources table already has new columns")
            
            # Check hashtags table
            result = conn.execute(text("SHOW TABLES LIKE 'hashtags'"))
            has_hashtags_table = result.fetchone() is not None
            
            if not has_hashtags_table:
                print("\nCreating hashtags table...")
                # Create hashtags table
                Base.metadata.create_all(bind=engine, tables=[Hashtag.__table__])
                print("[OK] Created hashtags table")
            else:
                print("[OK] hashtags table already exists")
            
            # Update raw_posts table
            result = conn.execute(text("SHOW COLUMNS FROM raw_posts LIKE 'hashtag_id'"))
            has_hashtag_id = result.fetchone() is not None
            
            if not has_hashtag_id:
                print("\nUpdating raw_posts table...")
                conn.execute(text("ALTER TABLE raw_posts MODIFY COLUMN source_id INT NULL"))
                conn.execute(text("ALTER TABLE raw_posts ADD COLUMN hashtag_id INT NULL"))
                conn.execute(text("ALTER TABLE raw_posts ADD COLUMN location VARCHAR(255)"))
                conn.execute(text("ALTER TABLE raw_posts ADD COLUMN is_kenyan BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE raw_posts ADD COLUMN media_url VARCHAR(500)"))
                conn.execute(text("CREATE INDEX idx_raw_post_location ON raw_posts(location)"))
                conn.execute(text("CREATE INDEX idx_raw_post_kenyan ON raw_posts(is_kenyan)"))
                print("[OK] Added new columns to raw_posts table")
            else:
                print("[OK] raw_posts table already has new columns")
            
            # Update stories table
            result = conn.execute(text("SHOW COLUMNS FROM stories LIKE 'is_kenyan'"))
            has_story_kenyan = result.fetchone() is not None
            
            if not has_story_kenyan:
                print("\nUpdating stories table...")
                conn.execute(text("ALTER TABLE stories ADD COLUMN location VARCHAR(255)"))
                conn.execute(text("ALTER TABLE stories ADD COLUMN is_kenyan BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE stories ADD COLUMN topic VARCHAR(255)"))
                conn.execute(text("CREATE INDEX idx_story_kenyan ON stories(is_kenyan)"))
                conn.execute(text("CREATE INDEX idx_story_location ON stories(location)"))
                print("[OK] Added new columns to stories table")
            else:
                print("[OK] stories table already has new columns")
            
            # Update scrape_logs table
            result = conn.execute(text("SHOW COLUMNS FROM scrape_logs LIKE 'hashtag_id'"))
            has_log_hashtag = result.fetchone() is not None
            
            if not has_log_hashtag:
                print("\nUpdating scrape_logs table...")
                conn.execute(text("ALTER TABLE scrape_logs MODIFY COLUMN source_id INT NULL"))
                conn.execute(text("ALTER TABLE scrape_logs ADD COLUMN hashtag_id INT NULL"))
                conn.execute(text("ALTER TABLE scrape_logs ADD COLUMN scrape_type VARCHAR(50) DEFAULT 'source'"))
                conn.execute(text("CREATE INDEX idx_scrape_log_hashtag ON scrape_logs(hashtag_id)"))
                print("[OK] Added new columns to scrape_logs table")
            else:
                print("[OK] scrape_logs table already has new columns")
            
            conn.commit()
            print("\n" + "=" * 60)
            print("[OK] Database schema updated successfully!")
            print("=" * 60)
            return True
            
    except Exception as e:
        logger.error(f"Error updating schema: {e}")
        print(f"\n[ERROR] {e}")
        print("\nTrying alternative method: recreating all tables...")
        
        try:
            # Alternative: Drop and recreate (WARNING: loses data)
            response = input("\nRecreate all tables? This will DELETE existing data! (yes/no): ")
            if response.lower() == 'yes':
                Base.metadata.drop_all(bind=engine)
                Base.metadata.create_all(bind=engine)
                print("[OK] All tables recreated")
                return True
            else:
                print("Cancelled. Please update schema manually.")
                return False
        except Exception as e2:
            print(f"[ERROR] {e2}")
            return False


if __name__ == "__main__":
    success = update_schema()
    sys.exit(0 if success else 1)
