"""Fix existing stories to have correct is_kenyan flags based on source."""
from database import SessionLocal
from models import Story, RawPost, Source
from loguru import logger
import sys


def fix_kenyan_flags():
    """Update existing stories with correct is_kenyan flags from sources."""
    db = SessionLocal()
    try:
        # Get all stories
        stories = db.query(Story).all()
        
        updated_count = 0
        for story in stories:
            # Get the raw_post
            raw_post = db.query(RawPost).filter(RawPost.id == story.raw_post_id).first()
            if not raw_post:
                continue
            
            # Get the source
            source = db.query(Source).filter(Source.id == raw_post.source_id).first()
            if not source:
                continue
            
            # Update story with source's is_kenyan and location
            needs_update = False
            
            if story.is_kenyan != source.is_kenyan:
                story.is_kenyan = source.is_kenyan
                needs_update = True
            
            if source.location and story.location != source.location:
                story.location = source.location
                needs_update = True
            
            # Also check content for Kenyan keywords
            content_lower = (story.content or "").lower()
            kenyan_keywords = ['kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila', 'kisumu']
            if not story.is_kenyan and any(kw in content_lower for kw in kenyan_keywords):
                story.is_kenyan = True
                if not story.location:
                    story.location = "Kenya"
                needs_update = True
            
            if needs_update:
                updated_count += 1
        
        db.commit()
        
        print(f"Updated {updated_count} stories with correct Kenyan flags")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error fixing Kenyan flags: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    """Fix Kenyan flags in existing stories."""
    print("=" * 60)
    print("Fixing Kenyan Flags in Existing Stories")
    print("=" * 60)
    print()
    
    updated = fix_kenyan_flags()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Stories updated: {updated}")
    print("\n[SUCCESS] Kenyan flags fixed!")
    print("\nNow when you filter by 'Local (Kenya)', you should see Kenyan stories.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
