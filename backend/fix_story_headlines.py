"""Fix story headlines to be more descriptive."""
from database import SessionLocal
from models import Story, RawPost
from loguru import logger

def main():
    """Fix headlines for existing stories."""
    print("=" * 60)
    print("Fixing Story Headlines")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        stories = db.query(Story).all()
        print(f"Found {len(stories)} stories\n")
        
        updated = 0
        for story in stories:
            # Get raw post content
            raw_post = db.query(RawPost).filter(RawPost.id == story.raw_post_id).first()
            
            if raw_post and raw_post.content:
                # Generate better headline
                content = raw_post.content.strip()
                
                # Try to extract first sentence or meaningful part
                if len(content) > 20:
                    # Take first 80 chars, clean it up
                    headline = content[:80].strip()
                    # Remove newlines and extra spaces
                    headline = " ".join(headline.split())
                    # Truncate at word boundary if needed
                    if len(headline) > 80:
                        headline = headline[:77] + "..."
                else:
                    headline = f"{story.author} on {story.platform}"
                
                # Update story
                old_headline = story.headline
                story.headline = headline
                updated += 1
                print(f"Updated story {story.id}:")
                print(f"  Old: {old_headline or '(empty)'}")
                print(f"  New: {headline}")
                print()
            else:
                # No content, use default
                if not story.headline:
                    story.headline = f"{story.author} on {story.platform}"
                    updated += 1
                    print(f"Set default headline for story {story.id}: {story.headline}")
        
        db.commit()
        
        print("=" * 60)
        print(f"[OK] Updated {updated} story headlines")
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
    import sys
    sys.exit(main())
