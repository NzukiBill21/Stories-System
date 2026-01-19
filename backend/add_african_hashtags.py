"""Add African and Kenyan hashtags for trending topic tracking."""
from database import SessionLocal
from models import Hashtag
from loguru import logger
import sys

# Kenyan and African hashtags for trending topics
AFRICAN_HASHTAGS = [
    # Kenyan Hashtags
    {'hashtag': '#Kenya', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#KenyaNews', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#Nairobi', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#Mombasa', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#KenyaTrending', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#KenyaPolitics', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#KenyaEntertainment', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#KenyaSports', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#NairobiTrending', 'platform': 'all', 'is_kenyan': True},
    {'hashtag': '#KenyaBreaking', 'platform': 'all', 'is_kenyan': True},
    
    # African Hashtags
    {'hashtag': '#Africa', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#AfricaNews', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#EastAfrica', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#WestAfrica', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#SouthAfrica', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#Nigeria', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#Ghana', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#Tanzania', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#Uganda', 'platform': 'all', 'is_kenyan': False},
    
    # Trending Topics
    {'hashtag': '#BreakingNews', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#Trending', 'platform': 'all', 'is_kenyan': False},
    {'hashtag': '#Viral', 'platform': 'all', 'is_kenyan': False},
]


def add_hashtags(db):
    """Add hashtags for tracking."""
    added = 0
    for hashtag_data in AFRICAN_HASHTAGS:
        # Check if hashtag already exists
        existing = db.query(Hashtag).filter(
            Hashtag.hashtag == hashtag_data['hashtag'],
            Hashtag.platform == hashtag_data['platform']
        ).first()
        
        if existing:
            existing.is_active = True  # Reactivate if exists
            logger.info(f"Hashtag already exists: {hashtag_data['hashtag']}")
            continue
        
        # Create new hashtag
        hashtag = Hashtag(
            hashtag=hashtag_data['hashtag'],
            platform=hashtag_data['platform'],
            is_active=True,
            is_kenyan=hashtag_data.get('is_kenyan', False),
            posts_per_hashtag=30  # Fetch more posts per hashtag
        )
        
        db.add(hashtag)
        added += 1
        logger.info(f"Added hashtag: {hashtag_data['hashtag']} ({hashtag_data['platform']})")
    
    return added


def main():
    """Add all African and Kenyan hashtags."""
    print("=" * 60)
    print("Adding African & Kenyan Hashtags for Trending Topics")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        print("Adding hashtags...")
        hashtags_added = add_hashtags(db)
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Hashtags added: {hashtags_added}")
        print("\n✅ All hashtags added!")
        print("\nThese hashtags will be tracked for trending topics.")
        print("\nNext step: Run hashtag scraping:")
        print("  python hashtag_scraper.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error adding hashtags: {e}")
        db.rollback()
        print(f"\n[ERROR] {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
