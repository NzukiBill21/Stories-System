"""Database connection and session management."""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config import settings
from loguru import logger

# Get MySQL connection URL
database_url = settings.get_database_url()

# Create engine with MySQL-specific settings
# For empty passwords, we need to ensure pymysql gets empty string
# SQLAlchemy URL format handles this, but we verify it works
engine = create_engine(
    database_url,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_size=10,         # Connection pool size
    max_overflow=20,       # Max overflow connections
    echo=False            # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            # Execute a simple query to test connection
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connected successfully")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing database connection: {e}")
        return False


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
