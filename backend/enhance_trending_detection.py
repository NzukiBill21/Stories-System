"""Enhance trending detection by re-scoring existing stories with new trending keywords."""
from database import SessionLocal
from models import Story, RawPost
from services import process_post_to_story
from loguru import logger
import sys


def enhance_trending_stories():
    """Re-process stories to apply enhanced trending detection."""
    db = SessionLocal()
    try:
        # Get all active stories
        stories = db.query(Story).filter(Story.is_active == True).all()
        
        updated = 0
        for story in stories:
            # Get the raw_post
            raw_post = db.query(RawPost).filter(RawPost.id == story.raw_post_id).first()
            if not raw_post:
                continue
            
            # Re-process to apply new scoring
            try:
                updated_story = process_post_to_story(db, raw_post)
                if updated_story and updated_story.score > story.score:
                    updated += 1
            except Exception as e:
                logger.error(f"Error re-processing story {story.id}: {e}")
                continue
        
        db.commit()
        print(f"Enhanced {updated} stories with improved trending detection")
        return updated
        
    except Exception as e:
        logger.error(f"Error enhancing stories: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    """Enhance trending detection."""
    print("=" * 60)
    print("Enhancing Trending Detection")
    print("=" * 60)
    print()
    print("Re-scoring stories with enhanced trending keywords...")
    
    updated = enhance_trending_stories()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Stories enhanced: {updated}")
    print("\n[SUCCESS] Trending detection enhanced!")
    print("\nStories with trending keywords now have higher scores.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
