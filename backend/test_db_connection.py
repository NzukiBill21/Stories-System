"""Test script to verify MySQL database connection."""
from database import test_connection, engine, Base
from models import Source, RawPost, Story, ScrapeLog
from config import settings
from loguru import logger
import sys


def main():
    """Test database connection and display connection info."""
    print("=" * 60)
    print("Story Intelligence Dashboard - Database Connection Test")
    print("=" * 60)
    print()
    
    # Display connection parameters (without password)
    print("Connection Parameters:")
    print(f"  Host: {settings.db_host}")
    print(f"  Port: {settings.db_port}")
    print(f"  User: {settings.db_user}")
    print(f"  Database: {settings.db_name}")
    print(f"  Password: {'*' * len(settings.db_password) if settings.db_password else '(empty)'}")
    print()
    
    # Test connection
    print("Testing connection...")
    connection_success = test_connection()
    if connection_success:
        print("✓ Database connected successfully")
        print()
        
        # Check if tables exist
        print("Checking database tables...")
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['sources', 'raw_posts', 'stories', 'scrape_logs']
            print(f"  Found {len(tables)} table(s) in database")
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✓ Table '{table}' exists")
                else:
                    print(f"  ✗ Table '{table}' not found")
            
            print()
            print("Database is ready to use!")
            return 0
        except Exception as e:
            logger.error(f"Error checking tables: {e}")
            print(f"  Warning: Could not check tables: {e}")
            print("  You may need to run 'python init_db.py' to create tables")
            return 0
    else:
        print("✗ Database connection failed")
        print()
        print("Troubleshooting:")
        print("  1. Check MySQL server is running")
        print("  2. Verify credentials in .env file:")
        print("     - DB_HOST")
        print("     - DB_USER")
        print("     - DB_PASSWORD")
        print("     - DB_NAME")
        print("  3. Ensure database exists:")
        print("     CREATE DATABASE story_intelligence;")
        print("  4. Check user has proper permissions")
        return 1


if __name__ == "__main__":
    sys.exit(main())
