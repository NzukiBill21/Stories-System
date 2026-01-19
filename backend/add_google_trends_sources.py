"""Add Google Trends sources for Kenya and global trending topics."""
from database import SessionLocal
from models import Source
from loguru import logger
import sys

# Google Trends sources (country codes)
GOOGLE_TRENDS_SOURCES = [
    {
        'name': 'Google Trends Kenya',
        'country_code': 'KE',  # Kenya
        'is_kenyan': True,
        'location': 'Kenya'
    },
    {
        'name': 'Google Trends Global',
        'country_code': 'US',  # Global (US as default)
        'is_kenyan': False,
        'location': None
    },
    {
        'name': 'Google Trends Africa',
        'country_code': 'ZA',  # South Africa (as proxy for Africa)
        'is_kenyan': False,
        'location': 'Africa'
    },
]


def add_google_trends_sources(db):
    """Add Google Trends sources."""
    added = 0
    for trend_source in GOOGLE_TRENDS_SOURCES:
        # Check if source already exists
        existing = db.query(Source).filter(
            Source.platform == 'GoogleTrends',
            Source.account_handle == trend_source['country_code']
        ).first()
        
        if existing:
            existing.is_active = True
            existing.is_kenyan = trend_source.get('is_kenyan', False)
            existing.location = trend_source.get('location')
            logger.info(f"Google Trends source already exists: {trend_source['name']}")
            continue
        
        # Create new source
        source = Source(
            platform='GoogleTrends',
            account_name=trend_source['name'],
            account_handle=trend_source['country_code'],
            account_id=None,
            is_active=True,
            is_kenyan=trend_source.get('is_kenyan', False),
            location=trend_source.get('location'),
            scrape_frequency_minutes=60  # Scrape every hour (Google Trends updates daily)
        )
        
        db.add(source)
        added += 1
        logger.info(f"Added Google Trends source: {trend_source['name']} ({trend_source['country_code']})")
    
    return added


def main():
    """Add Google Trends sources."""
    print("=" * 60)
    print("Adding Google Trends Sources")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        print("Adding Google Trends sources...")
        added = add_google_trends_sources(db)
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Google Trends sources added: {added}")
        print("\n[SUCCESS] All Google Trends sources added!")
        print("\nThese sources pull trending topics from Google Trends.")
        print("\nNext step: Run scraping:")
        print("  python auto_scrape_trending.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error adding sources: {e}")
        db.rollback()
        print(f"\n[ERROR] {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
