# Database Connection Fix Guide

## The Error

```
Access denied for user 'root'@'localhost' (using password: YES)
Error code: 1045
```

**Meaning:** The MySQL password in your `.env` file is incorrect.

## Quick Fix

### Step 1: Find Your MySQL Password

**Option A: You know your password**
- Use that password in `.env`

**Option B: You don't remember**
- Reset MySQL root password
- Or create a new MySQL user

### Step 2: Update .env File

Edit `backend/.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password_here  ← Update this!
DB_NAME=story_intelligence
```

### Step 3: Test Connection

```bash
cd backend
python fix_database_connection.py
```

Should show: `[OK] Connection successful!`

## Common Solutions

### Solution 1: Update Password in .env

1. Open `backend/.env`
2. Find `DB_PASSWORD=`
3. Replace with your actual MySQL password
4. Save file
5. Test: `python fix_database_connection.py`

### Solution 2: Create New MySQL User

If you can't remember root password:

```sql
-- In MySQL command line or Workbench
CREATE USER 'story_user'@'localhost' IDENTIFIED BY 'your_new_password';
GRANT ALL PRIVILEGES ON story_intelligence.* TO 'story_user'@'localhost';
FLUSH PRIVILEGES;
```

Then update `.env`:
```env
DB_USER=story_user
DB_PASSWORD=your_new_password
```

### Solution 3: Reset MySQL Root Password

**Windows:**
1. Stop MySQL service
2. Start MySQL in safe mode
3. Reset password
4. Restart MySQL

**Or use MySQL Workbench** to reset password.

### Solution 4: Check MySQL is Running

**Windows:**
```powershell
# Check if MySQL is running
Get-Service -Name MySQL*

# Start MySQL if not running
Start-Service -Name MySQL80  # or your MySQL service name
```

## Test Database Connection

Run:
```bash
python fix_database_connection.py
```

This will:
- ✅ Test current credentials
- ✅ Show what's wrong
- ✅ Give specific fix instructions

## After Fixing

Once connection works:

1. **Initialize database:**
   ```bash
   python init_db.py
   ```

2. **Configure sources:**
   ```bash
   python focus_facebook_tiktok.py
   ```

3. **Start scraping:**
   ```bash
   python trigger_scrape.py
   ```

## Quick Checklist

- [ ] MySQL is running
- [ ] Password in `.env` is correct
- [ ] Database `story_intelligence` exists (or will be created)
- [ ] User has permissions
- [ ] Test: `python fix_database_connection.py` shows success

## Summary

**The Issue:** Wrong MySQL password in `.env`

**The Fix:** Update `DB_PASSWORD` in `backend/.env` with your actual MySQL password

**Test:** `python fix_database_connection.py`

Once database works, you can proceed with Facebook and TikTok scraping! 🚀
