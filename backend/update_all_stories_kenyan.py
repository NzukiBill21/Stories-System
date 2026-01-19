"""Update all existing stories to detect Kenyan content from keywords."""
from database import SessionLocal
from models import Story, RawPost, Source
from loguru import logger
import sys


def update_stories_kenyan_flags():
    """Update all stories to detect Kenyan content from keywords and sources."""
    db = SessionLocal()
    try:
        stories = db.query(Story).all()
        
        kenyan_keywords = [
            'kenya', 'nairobi', 'mombasa', 'kenyan', 'ruto', 'raila', 
            'kisumu', 'nakuru', 'eldoret', 'kenya news', 'kenyan politics',
            'citizen tv', 'nation kenya', 'standard kenya', 'tuko kenya'
        ]
        
        african_keywords = [
            'africa', 'nigeria', 'south africa', 'ghana', 'tanzania', 
            'uganda', 'lagos', 'johannesburg', 'cairo', 'accra'
        ]
        
        updated_kenyan = 0
        updated_location = 0
        
        for story in stories:
            # Get raw_post and source
            raw_post = db.query(RawPost).filter(RawPost.id == story.raw_post_id).first()
            if raw_post:
                source = db.query(Source).filter(Source.id == raw_post.source_id).first()
                
                # Update from source
                if source:
                    if source.is_kenyan and not story.is_kenyan:
                        story.is_kenyan = True
                        updated_kenyan += 1
                    
                    if source.location and not story.location:
                        story.location = source.location
                        updated_location += 1
            
            # Detect from content
            content_lower = (story.content or "").lower()
            headline_lower = (story.headline or "").lower()
            combined = content_lower + " " + headline_lower
            
            # Check for Kenyan keywords
            if not story.is_kenyan:
                if any(kw in combined for kw in kenyan_keywords):
                    story.is_kenyan = True
                    if not story.location:
                        story.location = "Kenya"
                    updated_kenyan += 1
            
            # Check for African keywords (set location if not Kenyan)
            if not story.location:
                for kw in african_keywords:
                    if kw in combined:
                        if kw == 'nigeria':
                            story.location = "Nigeria"
                        elif kw == 'south africa':
                            story.location = "South Africa"
                        elif kw == 'ghana':
                            story.location = "Ghana"
                        elif kw == 'tanzania':
                            story.location = "Tanzania"
                        elif kw == 'uganda':
                            story.location = "Uganda"
                        elif kw == 'africa':
                            story.location = "Africa"
                        else:
                            story.location = kw.capitalize()
                        updated_location += 1
                        break
        
        db.commit()
        
        print(f"Updated {updated_kenyan} stories with Kenyan flag")
        print(f"Updated {updated_location} stories with location")
        return updated_kenyan
        
    except Exception as e:
        logger.error(f"Error updating stories: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    """Update all stories with Kenyan flags."""
    print("=" * 60)
    print("Updating All Stories with Kenyan Flags")
    print("=" * 60)
    print()
    
    updated = update_stories_kenyan_flags()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Stories updated: {updated}")
    print("\n[SUCCESS] All stories updated!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
