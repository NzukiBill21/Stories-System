# MySQL Migration Summary

The Python backend has been successfully updated to use MySQL instead of PostgreSQL.

## Changes Made

### 1. Database Driver (`requirements.txt`)
- ✅ Removed `psycopg2-binary` (PostgreSQL driver)
- ✅ Added `pymysql==1.1.0` (MySQL driver - pure Python, easy to install)
- ✅ Added `cryptography==41.0.7` (required for SSL connections)

### 2. Configuration (`config.py`)
- ✅ Added individual MySQL connection parameters:
  - `DB_HOST` (default: localhost)
  - `DB_PORT` (default: 3306)
  - `DB_USER` (default: root)
  - `DB_PASSWORD` (default: empty)
  - `DB_NAME` (default: story_intelligence)
- ✅ Added `get_database_url()` method to construct MySQL connection string
- ✅ Supports both individual parameters and full `DATABASE_URL` override

### 3. Database Connection (`database.py`)
- ✅ Updated to use MySQL connection string format: `mysql+pymysql://...`
- ✅ Added `test_connection()` function for connection testing
- ✅ Configured connection pooling optimized for MySQL:
  - Pool size: 10
  - Max overflow: 20
  - Connection recycling: 1 hour
  - Pre-ping enabled

### 4. Database Models (`models.py`)
- ✅ Removed `timezone=True` from DateTime columns (MySQL doesn't support timezone-aware datetimes)
- ✅ Added `ScrapeLog` model for tracking scraping operations
- ✅ All models compatible with MySQL

### 5. Initialization (`init_db.py`)
- ✅ Added connection testing before table creation
- ✅ Prints "Database connected successfully" on success
- ✅ Graceful error handling with helpful messages

### 6. Services (`services.py`)
- ✅ Added scrape logging functionality
- ✅ Creates `ScrapeLog` entries for each scraping operation
- ✅ Tracks success/error status, duration, and metrics

### 7. New Files Created
- ✅ `test_db_connection.py` - Standalone connection test script
- ✅ `env.example` - Example environment file with MySQL configuration
- ✅ `MYSQL_SETUP.md` - Complete MySQL setup guide

## Environment Variables

Add these to your `.env` file:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=story_intelligence
```

Or use full URL:

```env
DATABASE_URL=mysql+pymysql://user:password@host:port/database?charset=utf8mb4
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create MySQL database:**
   ```sql
   CREATE DATABASE story_intelligence CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Configure `.env` file** with your MySQL credentials

4. **Test connection:**
   ```bash
   python test_db_connection.py
   ```

5. **Initialize database:**
   ```bash
   python init_db.py
   ```

## Database Tables

The system creates four tables:

1. **sources** - Social media accounts to monitor
2. **raw_posts** - Raw posts fetched from platforms  
3. **stories** - Scored, filtered stories ready for dashboard
4. **scrape_logs** - Logging for scraping operations (NEW)

## Backward Compatibility

- ✅ All existing code continues to work
- ✅ API endpoints unchanged
- ✅ Service functions unchanged
- ✅ Models maintain same structure (except DateTime timezone)

## Testing

Run the test script to verify everything works:

```bash
python test_db_connection.py
```

Expected output:
```
✓ Database connected successfully
✓ Table 'sources' exists
✓ Table 'raw_posts' exists
✓ Table 'stories' exists
✓ Table 'scrape_logs' exists
```

## Notes

- MySQL uses `utf8mb4` charset for full Unicode support (including emojis)
- DateTime fields store UTC time but without timezone info (MySQL limitation)
- Connection pooling helps manage database connections efficiently
- Scrape logs provide visibility into scraping operations and errors

## Troubleshooting

See `MYSQL_SETUP.md` for detailed troubleshooting guide.

Common issues:
- **Connection refused**: MySQL server not running
- **Access denied**: Wrong credentials or insufficient permissions
- **Database doesn't exist**: Create it manually
- **Character encoding**: Ensure database uses `utf8mb4`

## Next Steps

1. Set up your MySQL database
2. Configure `.env` file with credentials
3. Run `python test_db_connection.py` to verify
4. Run `python init_db.py` to create tables
5. Start using the backend as normal!
