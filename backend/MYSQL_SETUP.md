# MySQL Database Setup Guide

This guide will help you set up MySQL for the Story Intelligence Dashboard backend.

## Prerequisites

- MySQL Server 5.7+ or MariaDB 10.3+
- Python 3.9+
- MySQL client tools (optional, for manual database creation)

## Step 1: Install MySQL Server

### Windows
1. Download MySQL Installer from https://dev.mysql.com/downloads/installer/
2. Run the installer and follow the setup wizard
3. Remember the root password you set during installation

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

### macOS
```bash
brew install mysql
brew services start mysql
```

## Step 2: Create Database

Connect to MySQL and create the database:

```bash
mysql -u root -p
```

Then run:
```sql
CREATE DATABASE story_intelligence CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'story_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON story_intelligence.* TO 'story_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Or if using root (not recommended for production):
```sql
CREATE DATABASE story_intelligence CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Step 3: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=story_user
DB_PASSWORD=your_secure_password
DB_NAME=story_intelligence

# Or use full URL (overrides individual settings above)
# DATABASE_URL=mysql+pymysql://story_user:password@localhost:3306/story_intelligence?charset=utf8mb4

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# ... other settings ...
```

## Step 4: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `pymysql` - Pure Python MySQL driver
- `cryptography` - Required for SSL connections
- `sqlalchemy` - ORM for database operations

## Step 5: Test Database Connection

Run the test script:

```bash
python test_db_connection.py
```

You should see:
```
✓ Database connected successfully
✓ Table 'sources' exists
✓ Table 'raw_posts' exists
✓ Table 'stories' exists
✓ Table 'scrape_logs' exists
```

## Step 6: Initialize Database Tables

Run the initialization script:

```bash
python init_db.py
```

This will:
1. Test the database connection
2. Create all required tables (sources, raw_posts, stories, scrape_logs)
3. Add sample sources to monitor

## Troubleshooting

### Connection Refused
- Check MySQL server is running:
  - Windows: Check Services panel
  - Linux: `sudo systemctl status mysql`
  - macOS: `brew services list`

### Access Denied
- Verify username and password in `.env`
- Check user has proper permissions:
  ```sql
  SHOW GRANTS FOR 'story_user'@'localhost';
  ```

### Database Doesn't Exist
- Create it manually:
  ```sql
  CREATE DATABASE story_intelligence CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

### Character Encoding Issues
- Ensure database uses `utf8mb4` charset:
  ```sql
  ALTER DATABASE story_intelligence CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

### Port Already in Use
- Check if MySQL is using default port 3306:
  ```bash
  netstat -an | grep 3306
  ```
- Update `DB_PORT` in `.env` if using a different port

### pymysql Installation Issues
- On Windows, you may need Visual C++ Build Tools
- Alternative: Use `mysqlclient` instead (requires MySQL development libraries)

## Database Schema

The system creates four main tables:

1. **sources** - Social media accounts to monitor
2. **raw_posts** - Raw posts fetched from platforms
3. **stories** - Scored, filtered stories ready for dashboard
4. **scrape_logs** - Logging for scraping operations

## Connection Pooling

The database connection uses SQLAlchemy's connection pooling:
- Pool size: 10 connections
- Max overflow: 20 connections
- Connection recycling: Every hour
- Pre-ping: Enabled (verifies connections before use)

## Production Considerations

1. **Use a dedicated database user** (not root)
2. **Set strong passwords** for database users
3. **Enable SSL** for remote connections
4. **Configure firewall** to restrict database access
5. **Set up regular backups**
6. **Monitor connection pool usage**
7. **Use connection string with SSL** if connecting remotely:
   ```env
   DATABASE_URL=mysql+pymysql://user:pass@host:3306/db?ssl_ca=/path/to/ca.pem
   ```

## Verification

After setup, verify everything works:

```bash
# Test connection
python test_db_connection.py

# Initialize database
python init_db.py

# Start API server (should connect automatically)
python main.py
```

The API will automatically connect to MySQL when it starts.
