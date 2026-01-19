# Quick Start: Automatic Scraping 🚀

## What You Need to Know

Your system now **automatically scrapes sources** based on their `scrape_frequency_minutes` setting!

## How to Start

**Just start the API server - that's it!**

```bash
cd backend
python main.py
```

The background scheduler starts automatically and begins scraping.

## How It Works

1. **Background Scheduler:**
   - Checks every 1 minute which sources need scraping
   - Scrapes sources based on their `scrape_frequency_minutes` setting
   - Updates `last_checked_at` after each scrape

2. **Source Settings:**
   - Each source has a `scrape_frequency_minutes` field
   - Examples:
     - `10` = scrapes every 10 minutes
     - `30` = scrapes every 30 minutes  
     - `60` = scrapes every hour
     - `1440` = scrapes daily

3. **Dashboard:**
   - Refresh your dashboard to see new stories
   - Stories are automatically ordered by engagement velocity (trending first)

## Check Status

```bash
curl http://localhost:8001/api/scheduler/status
```

## View Logs

Watch the API server console to see scraping activity:
```
INFO: Auto-scraping RSS: BBC News (frequency: 30 min)
INFO:   ✓ BBC News: 4 posts, 1 stories
```

## Configure Frequency

Update a source's scraping frequency in the database or via API.

**That's it! Your system now automatically pulls new stories!** 📰✨
