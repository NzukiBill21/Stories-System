"""
Add RSS feed sources that work WITHOUT any API keys.
Run this so you get stories even if Twitter/Facebook/Instagram/TikTok are not configured.

Usage: cd backend && python add_rss_sources.py
"""
from database import SessionLocal, test_connection
from models import Source
from loguru import logger
import sys

RSS_SOURCES = [
    {
        "platform": "RSS",
        "account_handle": "https://feeds.bbci.co.uk/news/rss.xml",
        "account_name": "BBC News",
        "is_trusted": True,
        "is_kenyan": False,
    },
    {
        "platform": "RSS",
        "account_handle": "http://rss.cnn.com/rss/cnn_topstories.rss",
        "account_name": "CNN Top Stories",
        "is_trusted": True,
        "is_kenyan": False,
    },
    {
        "platform": "RSS",
        "account_handle": "https://feeds.reuters.com/reuters/topNews",
        "account_name": "Reuters Top News",
        "is_trusted": True,
        "is_kenyan": False,
    },
    {
        "platform": "RSS",
        "account_handle": "https://www.theguardian.com/world/rss",
        "account_name": "The Guardian World",
        "is_trusted": True,
        "is_kenyan": False,
    },
]


def main():
    if not test_connection():
        print("Database connection failed. Check MySQL and .env")
        sys.exit(1)

    db = SessionLocal()
    added = 0
    try:
        for s in RSS_SOURCES:
            existing = db.query(Source).filter(
                Source.platform == "RSS",
                Source.account_handle == s["account_handle"],
            ).first()
            if existing:
                logger.info(f"Already have: {s['account_name']}")
                continue
            source = Source(
                platform=s["platform"],
                account_handle=s["account_handle"],
                account_name=s["account_name"],
                is_active=True,
                is_trusted=s["is_trusted"],
                is_kenyan=s.get("is_kenyan", False),
                scrape_frequency_minutes=30,
            )
            db.add(source)
            added += 1
            print(f"  Added: {s['account_name']}")

        db.commit()
        print(f"\nDone. Added {added} RSS source(s).")
        if added > 0:
            print("Stories will appear after the next scrape (within ~1 min) or trigger scrape from Sources in the app.")
    except Exception as e:
        logger.error(e)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
