"""Initialize database with sample sources."""
from database import SessionLocal, engine, Base, test_connection
from models import Source, ScrapeLog
from loguru import logger
import sys


def init_database():
    """Create tables and add sample sources."""
    # Test database connection first
    logger.info("Testing database connection...")
    if not test_connection():
        logger.error("Failed to connect to database. Please check your .env configuration.")
        print("Database connection failed. Please check your .env file:")
        print("  - DB_HOST")
        print("  - DB_USER")
        print("  - DB_PASSWORD")
        print("  - DB_NAME")
        sys.exit(1)
    
    print("Database connected successfully")
    
    # Create all tables
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        print("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        print(f"Error creating tables: {e}")
        sys.exit(1)
    
    db = SessionLocal()
    try:
        # Check if sources already exist
        existing = db.query(Source).count()
        if existing > 0:
            logger.info(f"Database already has {existing} sources. Skipping initialization.")
            return
        
        # Add sample sources
        sample_sources = [
            Source(
                platform="X",
                account_handle="@BBCNews",
                account_name="BBC News",
                is_active=True,
                is_trusted=True,
                scrape_frequency_minutes=15
            ),
            Source(
                platform="X",
                account_handle="@CNN",
                account_name="CNN",
                is_active=True,
                is_trusted=True,
                scrape_frequency_minutes=15
            ),
            Source(
                platform="X",
                account_handle="@Reuters",
                account_name="Reuters",
                is_active=True,
                is_trusted=True,
                scrape_frequency_minutes=15
            ),
            Source(
                platform="Facebook",
                account_handle="BBCNews",
                account_name="BBC News",
                is_active=True,
                is_trusted=True,
                scrape_frequency_minutes=30
            ),
            Source(
                platform="Instagram",
                account_handle="bbcnews",
                account_name="BBC News",
                is_active=True,
                is_trusted=True,
                scrape_frequency_minutes=30
            ),
            Source(
                platform="TikTok",
                account_handle="trending",
                account_name="TikTok Trending",
                is_active=True,
                is_trusted=False,
                scrape_frequency_minutes=30
            ),
        ]
        
        for source in sample_sources:
            db.add(source)
        
        db.commit()
        logger.info(f"Added {len(sample_sources)} sample sources")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
