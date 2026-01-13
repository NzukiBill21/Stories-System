# Start MySQL Before Running Scraping

## Issue
MySQL server is not running. The scraping script needs MySQL to store data.

## Solution

### Windows (XAMPP/WAMP)
1. Open XAMPP Control Panel or WAMP
2. Click "Start" for MySQL
3. Wait for MySQL to start (green indicator)

### Windows (MySQL Service)
1. Open Services (Win+R, type `services.msc`)
2. Find "MySQL" service
3. Right-click → Start

### Command Line (if MySQL is in PATH)
```bash
net start MySQL
```

## Then Run Scraping

After MySQL is running:
```bash
python scrape_facebook_trends.py
```
