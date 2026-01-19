"""Update stories directly using Python ORM."""
from database import SessionLocal
from models import Story, RawPost, Source
from loguru import logger
import sys


def update_stories():
    """Update stories to have correct Kenyan flags."""
    db = SessionLocal()
    try:
        # Get all stories
        stories = db.query(Story).all()
        
        updated = 0
        for story in stories:
            # Get raw_post
            raw_post = db.query(RawPost).filter(RawPost.id == story.raw_post_id).first()
            if not raw_post:
                continue
            
            # Get source
            source = db.query(Source).filter(Source.id == raw_post.source_id).first()
            if not source:
                continue
            
            # Check if source is Kenyan
            if source.is_kenyan and not story.is_kenyan:
                story.is_kenyan = True
                if not story.location:
                    story.location = source.location or "Kenya"
                updated += 1
                continue
            
            # Check source name/handle for Kenyan keywords
            source_name_lower = (source.account_name or "").lower()
            source_handle_lower = (source.account_handle or "").lower()
            
            if ('kenya' in source_name_lower or 'kenya' in source_handle_lower or
                'nairobi' in source_name_lower or source.account_handle in ['Kenya', 'Nairobi']):
                if not story.is_kenyan:
                    story.is_kenyan = True
                    if not story.location:
                        story.location = "Kenya"
                    updated += 1
                    continue
            
            # Check content for Kenyan keywords
            content = ((story.content or "") + " " + (story.headline or "")).lower()
            kenyan_keywords = ['kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila', 'kisumu']
            
            if any(kw in content for kw in kenyan_keywords):
                if not story.is_kenyan:
                    story.is_kenyan = True
                    if not story.location:
                        story.location = "Kenya"
                    updated += 1
        
        db.commit()
        return updated
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    """Update stories."""
    print("=" * 60)
    print("Updating Stories with Kenyan Flags")
    print("=" * 60)
    print()
    
    updated = update_stories()
    
    # Check count
    from models import Story
    db = SessionLocal()
    kenyan_count = db.query(Story).filter(Story.is_kenyan == True).count()
    total = db.query(Story).count()
    db.close()
    
    print(f"\nUpdated {updated} stories")
    print(f"Kenyan stories: {kenyan_count}/{total}")
    print("\n[SUCCESS] Done!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
