"""
Process raw posts to stories after trend aggregation.

This script processes all unprocessed raw posts and creates stories.
Run this after scraping Facebook trends to convert raw_posts to stories.
"""
from database import SessionLocal, test_connection
from models import RawPost, Story
from services import process_post_to_story
from loguru import logger
import sys


def main():
    """Process raw posts to stories."""
    print("=" * 60)
    print("Process Raw Posts to Stories")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    db = SessionLocal()
    try:
        # Get all raw posts that haven't been processed to stories
        raw_posts = db.query(RawPost).filter(
            ~RawPost.id.in_(
                db.query(Story.raw_post_id).filter(Story.raw_post_id.isnot(None))
            )
        ).all()
        
        if not raw_posts:
            print("[INFO] No unprocessed raw posts found")
            return 0
        
        print(f"Found {len(raw_posts)} unprocessed raw post(s)")
        print()
        
        stories_created = 0
        for raw_post in raw_posts:
            try:
                story = process_post_to_story(db, raw_post)
                if story:
                    stories_created += 1
                    print(f"  [OK] Created story from {raw_post.platform} post (Score: {story.score:.1f})")
            except Exception as e:
                logger.error(f"Error processing post {raw_post.id}: {e}")
                print(f"  [ERROR] Failed to process post {raw_post.id}: {e}")
        
        db.commit()
        
        print()
        print("=" * 60)
        print(f"[OK] Created {stories_created} story/stories from {len(raw_posts)} raw post(s)")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        db.rollback()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
