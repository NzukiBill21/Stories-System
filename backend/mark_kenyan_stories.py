"""Mark stories as Kenyan based on source and content."""
from database import SessionLocal
from models import Story, RawPost, Source
from loguru import logger
import sys


def mark_kenyan_stories():
    """Mark stories as Kenyan based on source and content."""
    db = SessionLocal()
    try:
        # Get all stories with their raw_posts and sources
        stories = db.query(Story).join(RawPost).join(Source).all()
        
        kenyan_sources = ['Kenya', 'Nairobi', 'Nation Media Kenya', 'Standard Media Kenya', 
                         'Citizen TV Kenya', 'TUKO News Kenya', 'The Star Kenya', 
                         'Business Daily Kenya', 'BBC Africa', 'CNN Africa']
        
        kenyan_keywords = ['kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila', 
                          'kisumu', 'nakuru', 'eldoret', 'kenya news', 'kenyan politics']
        
        updated = 0
        
        for story in stories:
            raw_post = db.query(RawPost).filter(RawPost.id == story.raw_post_id).first()
            if not raw_post:
                continue
            
            source = db.query(Source).filter(Source.id == raw_post.source_id).first()
            if not source:
                continue
            
            # Check source
            is_kenyan_source = (
                source.is_kenyan or 
                source.account_name in kenyan_sources or
                source.account_handle in ['Kenya', 'Nairobi'] or
                'kenya' in (source.account_name or '').lower() or
                'kenya' in (source.account_handle or '').lower()
            )
            
            # Check content
            content = (story.content or "").lower() + " " + (story.headline or "").lower()
            has_kenyan_keywords = any(kw in content for kw in kenyan_keywords)
            
            if (is_kenyan_source or has_kenyan_keywords) and not story.is_kenyan:
                story.is_kenyan = True
                if not story.location:
                    story.location = "Kenya"
                updated += 1
        
        db.commit()
        print(f"Marked {updated} stories as Kenyan")
        return updated
        
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    """Mark Kenyan stories."""
    print("=" * 60)
    print("Marking Kenyan Stories")
    print("=" * 60)
    print()
    
    updated = mark_kenyan_stories()
    
    print(f"\nUpdated {updated} stories")
    
    # Check count
    from models import Story
    db = SessionLocal()
    kenyan_count = db.query(Story).filter(Story.is_kenyan == True).count()
    total = db.query(Story).count()
    db.close()
    
    print(f"\nKenyan stories: {kenyan_count}/{total}")
    print("\n[SUCCESS] Done!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
