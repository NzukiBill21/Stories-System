"""Initialize database with Kenyan sources and hashtags."""
from database import SessionLocal, engine, Base, test_connection
from models import Source, Hashtag
from kenyan_sources_config import (
    get_all_sources, 
    KENYAN_HASHTAGS,
    GLOBAL_SOURCES,
    KENYAN_SOURCES
)
from loguru import logger
import sys


def init_kenyan_sources():
    """Initialize Kenyan sources and hashtags in database."""
    # Test database connection
    if not test_connection():
        logger.error("Database connection failed")
        print("Database connection failed. Please check your .env configuration.")
        sys.exit(1)
    
    print("Database connected successfully")
    
    # Create all tables (including new Hashtag table)
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        print(f"Error creating tables: {e}")
        sys.exit(1)
    
    db = SessionLocal()
    try:
        # Add sources
        all_sources_config = get_all_sources()
        sources_added = 0
        
        for source_config in all_sources_config:
            # Check if source already exists
            existing = db.query(Source).filter(
                Source.platform == source_config.platform,
                Source.account_handle == source_config.account_handle
            ).first()
            
            if existing:
                # Update existing source
                existing.account_name = source_config.account_name
                existing.account_id = source_config.account_id or existing.account_id
                existing.is_trusted = source_config.is_trusted
                existing.is_kenyan = source_config.is_kenyan
                existing.location = source_config.location
                existing.scrape_frequency_minutes = source_config.scrape_frequency_minutes
                existing.is_active = True
                logger.info(f"Updated source: {source_config.account_handle}")
            else:
                # Create new source
                source = Source(
                    platform=source_config.platform,
                    account_handle=source_config.account_handle,
                    account_name=source_config.account_name,
                    account_id=source_config.account_id,
                    is_active=True,
                    is_trusted=source_config.is_trusted,
                    is_kenyan=source_config.is_kenyan,
                    location=source_config.location,
                    scrape_frequency_minutes=source_config.scrape_frequency_minutes
                )
                db.add(source)
                sources_added += 1
                logger.info(f"Added source: {source_config.account_handle}")
        
        # Add hashtags
        hashtags_added = 0
        
        for hashtag_config in KENYAN_HASHTAGS:
            # Check if hashtag already exists
            existing = db.query(Hashtag).filter(
                Hashtag.hashtag == hashtag_config.hashtag
            ).first()
            
            if existing:
                # Update existing hashtag
                existing.platform = hashtag_config.platform
                existing.is_kenyan = hashtag_config.is_kenyan
                existing.posts_per_hashtag = hashtag_config.posts_per_hashtag
                existing.min_engagement = hashtag_config.min_engagement
                existing.is_active = True
                logger.info(f"Updated hashtag: {hashtag_config.hashtag}")
            else:
                # Create new hashtag
                hashtag = Hashtag(
                    hashtag=hashtag_config.hashtag,
                    platform=hashtag_config.platform,
                    is_kenyan=hashtag_config.is_kenyan,
                    is_active=True,
                    posts_per_hashtag=hashtag_config.posts_per_hashtag,
                    min_engagement=hashtag_config.min_engagement
                )
                db.add(hashtag)
                hashtags_added += 1
                logger.info(f"Added hashtag: {hashtag_config.hashtag}")
        
        db.commit()
        
        print(f"\n✓ Added/updated {sources_added} sources")
        print(f"✓ Added/updated {hashtags_added} hashtags")
        print(f"\nTotal sources: {len(all_sources_config)}")
        print(f"  - Global sources: {len(GLOBAL_SOURCES)}")
        print(f"  - Kenyan sources: {len(KENYAN_SOURCES)}")
        print(f"\nTotal hashtags: {len(KENYAN_HASHTAGS)}")
        print("\nKenyan sources include:")
        for source in KENYAN_SOURCES:
            print(f"  - {source.platform}: {source.account_handle} ({source.account_name})")
        print("\nKenyan hashtags include:")
        for hashtag in KENYAN_HASHTAGS[:5]:  # Show first 5
            print(f"  - {hashtag.hashtag}")
        if len(KENYAN_HASHTAGS) > 5:
            print(f"  ... and {len(KENYAN_HASHTAGS) - 5} more")
        
        print("\n✅ Kenyan sources and hashtags initialized successfully!")
        print("\nNext steps:")
        print("  1. Update Facebook/Instagram account IDs in database")
        print("  2. Run 'python trigger_scrape.py' to fetch data")
        print("  3. Check dashboard for Kenyan stories!")
        
    except Exception as e:
        logger.error(f"Error initializing Kenyan sources: {e}")
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_kenyan_sources()
