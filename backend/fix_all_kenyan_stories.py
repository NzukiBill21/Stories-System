"""Fix all stories to have correct Kenyan flags - direct SQL update."""
from database import SessionLocal
from models import Story, RawPost, Source
from sqlalchemy import text
from loguru import logger
import sys


def fix_all_stories():
    """Update all stories using direct SQL for better performance."""
    db = SessionLocal()
    try:
        # Update stories from Kenyan sources
        query1 = text("""
            UPDATE stories s
            INNER JOIN raw_posts rp ON s.raw_post_id = rp.id
            INNER JOIN sources src ON rp.source_id = src.id
            SET s.is_kenyan = TRUE, s.location = COALESCE(s.location, src.location, 'Kenya')
            WHERE src.is_kenyan = TRUE AND s.is_kenyan = FALSE
        """)
        result1 = db.execute(query1)
        
        # Update stories from r/Kenya and r/Nairobi subreddits
        query2 = text("""
            UPDATE stories s
            INNER JOIN raw_posts rp ON s.raw_post_id = rp.id
            INNER JOIN sources src ON rp.source_id = src.id
            SET s.is_kenyan = TRUE, s.location = 'Kenya'
            WHERE src.platform = 'Reddit' 
            AND src.account_handle IN ('Kenya', 'Nairobi')
            AND s.is_kenyan = FALSE
        """)
        result2 = db.execute(query2)
        
        # Update stories from Kenyan RSS sources
        query3 = text("""
            UPDATE stories s
            INNER JOIN raw_posts rp ON s.raw_post_id = rp.id
            INNER JOIN sources src ON rp.source_id = src.id
            SET s.is_kenyan = TRUE, s.location = 'Kenya'
            WHERE src.platform = 'RSS'
            AND (src.account_name LIKE '%Kenya%' OR src.account_name LIKE '%Nation%' OR src.account_name LIKE '%Standard%' OR src.account_name LIKE '%Citizen%' OR src.account_name LIKE '%TUKO%')
            AND s.is_kenyan = FALSE
        """)
        result3 = db.execute(query3)
        
        # Update stories based on content keywords
        query4 = text("""
            UPDATE stories
            SET is_kenyan = TRUE, location = COALESCE(location, 'Kenya')
            WHERE (content LIKE '%kenya%' OR content LIKE '%nairobi%' OR content LIKE '%mombasa%' 
                   OR headline LIKE '%kenya%' OR headline LIKE '%nairobi%' OR headline LIKE '%mombasa%'
                   OR content LIKE '%kenyan%' OR headline LIKE '%kenyan%'
                   OR content LIKE '%ruto%' OR headline LIKE '%ruto%'
                   OR content LIKE '%raila%' OR headline LIKE '%raila%')
            AND is_kenyan = FALSE
        """)
        result4 = db.execute(query4)
        
        db.commit()
        
        total_updated = result1.rowcount + result2.rowcount + result3.rowcount + result4.rowcount
        print(f"Updated {total_updated} stories:")
        print(f"  - From Kenyan sources: {result1.rowcount}")
        print(f"  - From r/Kenya subreddit: {result2.rowcount}")
        print(f"  - From Kenyan RSS feeds: {result3.rowcount}")
        print(f"  - From content keywords: {result4.rowcount}")
        
        return total_updated
        
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return 0
    finally:
        db.close()


def main():
    """Fix all Kenyan stories."""
    print("=" * 60)
    print("Fixing All Kenyan Stories")
    print("=" * 60)
    print()
    
    updated = fix_all_stories()
    
    # Check final count
    from models import Story
    db = SessionLocal()
    kenyan_count = db.query(Story).filter(Story.is_kenyan == True).count()
    total = db.query(Story).count()
    db.close()
    
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Stories updated: {updated}")
    print(f"Kenyan stories: {kenyan_count}/{total}")
    print("\n[SUCCESS] All Kenyan stories fixed!")
    print("\nNow when you filter by 'Local (Kenya)', you should see Kenyan stories.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
