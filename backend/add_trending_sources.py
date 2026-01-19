"""Add trending sources that don't require authentication."""
from database import SessionLocal
from models import Source
from loguru import logger
import sys

# Trending RSS feeds (no auth required)
RSS_FEEDS = [
    # Global News
    {
        'name': 'BBC News',
        'url': 'http://feeds.bbci.co.uk/news/rss.xml',
        'is_kenyan': False
    },
    {
        'name': 'BBC Africa',
        'url': 'http://feeds.bbci.co.uk/news/world/africa/rss.xml',
        'is_kenyan': False,
        'location': 'Africa'
    },
    {
        'name': 'CNN Top Stories',
        'url': 'http://rss.cnn.com/rss/edition.rss',
        'is_kenyan': False
    },
    {
        'name': 'CNN Africa',
        'url': 'http://rss.cnn.com/rss/edition_africa.rss',
        'is_kenyan': False,
        'location': 'Africa'
    },
    {
        'name': 'Reuters Top News',
        'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
        'is_kenyan': False
    },
    {
        'name': 'Reuters Africa',
        'url': 'https://www.reuters.com/world/africa/',
        'is_kenyan': False,
        'location': 'Africa'
    },
    # Kenyan News Sources
    {
        'name': 'Nation Media Kenya',
        'url': 'https://www.nation.co.ke/rss',
        'is_kenyan': True,
        'location': 'Kenya'
    },
    {
        'name': 'Standard Media Kenya',
        'url': 'https://www.standardmedia.co.ke/rss',
        'is_kenyan': True,
        'location': 'Kenya'
    },
    {
        'name': 'Citizen TV Kenya',
        'url': 'https://citizentv.co.ke/rss',
        'is_kenyan': True,
        'location': 'Kenya'
    },
    {
        'name': 'TUKO News Kenya',
        'url': 'https://www.tuko.co.ke/rss',
        'is_kenyan': True,
        'location': 'Kenya'
    },
    {
        'name': 'The Star Kenya',
        'url': 'https://www.the-star.co.ke/rss',
        'is_kenyan': True,
        'location': 'Kenya'
    },
    {
        'name': 'Business Daily Kenya',
        'url': 'https://www.businessdailyafrica.com/rss',
        'is_kenyan': True,
        'location': 'Kenya'
    },
    # African News Sources
    {
        'name': 'AllAfrica',
        'url': 'https://allafrica.com/tools/headlines/rdf/kenya/headlines.rdf',
        'is_kenyan': True,
        'location': 'Africa'
    },
    {
        'name': 'Africa News',
        'url': 'https://www.africanews.com/rss',
        'is_kenyan': False,
        'location': 'Africa'
    },
]

# Trending Reddit subreddits (no auth required)
REDDIT_SUBREDDITS = [
    # Global
    {
        'name': 'World News',
        'subreddit': 'worldnews',
        'is_kenyan': False
    },
    {
        'name': 'News',
        'subreddit': 'news',
        'is_kenyan': False
    },
    {
        'name': 'Technology',
        'subreddit': 'technology',
        'is_kenyan': False
    },
    {
        'name': 'Uplifting News',
        'subreddit': 'UpliftingNews',
        'is_kenyan': False
    },
    # Kenyan & African
    {
        'name': 'Kenya',
        'subreddit': 'Kenya',
        'is_kenyan': True,
        'location': 'Kenya'
    },
    {
        'name': 'Nairobi',
        'subreddit': 'Nairobi',
        'is_kenyan': True,
        'location': 'Nairobi, Kenya'
    },
    {
        'name': 'South Africa',
        'subreddit': 'southafrica',
        'is_kenyan': False,
        'location': 'South Africa'
    },
    {
        'name': 'Nigeria',
        'subreddit': 'Nigeria',
        'is_kenyan': False,
        'location': 'Nigeria'
    },
    {
        'name': 'Ghana',
        'subreddit': 'ghana',
        'is_kenyan': False,
        'location': 'Ghana'
    },
    {
        'name': 'Tanzania',
        'subreddit': 'tanzania',
        'is_kenyan': False,
        'location': 'Tanzania'
    },
    {
        'name': 'Uganda',
        'subreddit': 'Uganda',
        'is_kenyan': False,
        'location': 'Uganda'
    },
    {
        'name': 'Africa',
        'subreddit': 'Africa',
        'is_kenyan': False,
        'location': 'Africa'
    },
]


def add_rss_sources(db):
    """Add RSS feed sources."""
    added = 0
    for feed in RSS_FEEDS:
        # Check if source already exists
        existing = db.query(Source).filter(
            Source.platform == 'RSS',
            Source.account_handle == feed['url']
        ).first()
        
        if existing:
            logger.info(f"RSS source already exists: {feed['name']}")
            continue
        
        # Create new source
        source = Source(
            platform='RSS',
            account_name=feed['name'],
            account_handle=feed['url'],
            account_id=None,
            is_active=True,
            is_kenyan=feed.get('is_kenyan', False),
            location=feed.get('location'),
            scrape_frequency_minutes=30  # Scrape every 30 minutes
        )
        
        db.add(source)
        added += 1
        logger.info(f"Added RSS source: {feed['name']}")
    
    return added


def add_reddit_sources(db):
    """Add Reddit subreddit sources."""
    added = 0
    for sub in REDDIT_SUBREDDITS:
        # Check if source already exists
        existing = db.query(Source).filter(
            Source.platform == 'Reddit',
            Source.account_handle == sub['subreddit']
        ).first()
        
        if existing:
            logger.info(f"Reddit source already exists: {sub['name']}")
            continue
        
        # Create new source
        source = Source(
            platform='Reddit',
            account_name=sub['name'],
            account_handle=sub['subreddit'],
            account_id=None,
            is_active=True,
            is_kenyan=sub.get('is_kenyan', False),
            location=sub.get('location'),
            scrape_frequency_minutes=30  # Scrape every 30 minutes
        )
        
        db.add(source)
        added += 1
        logger.info(f"Added Reddit source: {sub['name']} (r/{sub['subreddit']})")
    
    return added


def ensure_tiktok_source(db):
    """Ensure TikTok trending source exists."""
    existing = db.query(Source).filter(
        Source.platform == 'TikTok',
        Source.account_handle == 'trending'
    ).first()
    
    if existing:
        existing.is_active = True
        logger.info("TikTok trending source already exists and is active")
        return 0
    
    # Create TikTok trending source
    source = Source(
        platform='TikTok',
        account_name='TikTok Trending',
        account_handle='trending',
        account_id=None,
        is_active=True,
        is_kenyan=False,
        scrape_frequency_minutes=30
    )
    
    db.add(source)
    logger.info("Added TikTok trending source")
    return 1


def main():
    """Add all trending sources."""
    print("=" * 60)
    print("Adding Trending Sources (No Authentication Required)")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Add RSS feeds
        print("Adding RSS feeds...")
        rss_added = add_rss_sources(db)
        
        # Add Reddit subreddits
        print("\nAdding Reddit subreddits...")
        reddit_added = add_reddit_sources(db)
        
        # Ensure TikTok source exists
        print("\nEnsuring TikTok trending source...")
        tiktok_added = ensure_tiktok_source(db)
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"RSS feeds added: {rss_added}")
        print(f"Reddit subreddits added: {reddit_added}")
        print(f"TikTok sources added: {tiktok_added}")
        print(f"\nTotal new sources: {rss_added + reddit_added + tiktok_added}")
        print("\n✅ All trending sources added!")
        print("\nThese sources don't require authentication and will pull trending content.")
        print("\nNext step: Run scraping:")
        print("  python trigger_scrape_now.py")
        
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
