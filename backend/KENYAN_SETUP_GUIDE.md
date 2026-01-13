# Kenyan Content Scraping Setup Guide

## Overview

The system now supports scraping high-engagement content from TikTok, Instagram, and Facebook with a focus on both global and local Kenyan trends.

## Features

✅ **Global Sources**: BBC, CNN, Reuters  
✅ **Kenyan Sources**: Nation Africa, Standard Digital, Tuko News  
✅ **Hashtag Tracking**: #KenyaElections, #Nairobi, #Mombasa, #TrendingKenya, etc.  
✅ **Location Filtering**: Nairobi, Mombasa, Kisumu, and other Kenyan locations  
✅ **High-Engagement Only**: Filters out low-impact content automatically  
✅ **Kenyan Content Priority**: Kenyan stories appear first in dashboard  
✅ **Topic Classification**: Politics, Entertainment, Sports, Tech  

## Quick Start

### Step 1: Initialize Kenyan Sources

```bash
cd backend
python init_kenyan_sources.py
```

This will:
- Create/update database tables (including new `hashtags` table)
- Add global sources (BBC, CNN, Reuters)
- Add Kenyan sources (Nation, Standard, Tuko)
- Add Kenyan hashtags to track
- Mark sources with `is_kenyan` flag

### Step 2: Update Facebook/Instagram Account IDs

You need to get numeric IDs for Facebook pages and Instagram accounts:

```python
from database import SessionLocal
from models import Source

db = SessionLocal()

# Update Facebook page ID
fb = db.query(Source).filter(Source.platform == "Facebook").first()
fb.account_id = "YOUR_FACEBOOK_PAGE_ID"  # Get from Graph API Explorer

# Update Instagram account ID
ig = db.query(Source).filter(Source.platform == "Instagram").first()
ig.account_id = "YOUR_INSTAGRAM_ACCOUNT_ID"  # Get from Graph API Explorer

db.commit()
```

### Step 3: Test Scraping

```bash
# Test source-based scraping
python trigger_scrape.py

# Test hashtag-based scraping (if implemented)
python -c "from database import SessionLocal; from hashtag_scraper import scrape_hashtag; from models import Hashtag; db = SessionLocal(); h = db.query(Hashtag).first(); print(scrape_hashtag(db, h.id))"
```

### Step 4: Start Services

```bash
# Terminal 1: API Server
python main.py

# Terminal 2: Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 3: Celery Beat (Scheduler)
celery -A celery_app beat --loglevel=info
```

## Configuration

### Kenyan Sources

Edit `backend/kenyan_sources_config.py` to add more sources:

```python
KENYAN_SOURCES = [
    SourceConfig(
        platform="X",
        account_handle="@YourAccount",
        account_name="Your Account Name",
        is_kenyan=True,
        location="Nairobi",
        scrape_frequency_minutes=15
    ),
]
```

### Kenyan Hashtags

Edit `backend/kenyan_sources_config.py` to add more hashtags:

```python
KENYAN_HASHTAGS = [
    HashtagConfig(
        hashtag="#YourHashtag",
        platform="all",  # or "X", "Instagram", "Facebook", "TikTok"
        is_kenyan=True,
        posts_per_hashtag=20,
        min_engagement=100
    ),
]
```

### Kenyan Keywords

Edit `backend/kenyan_sources_config.py` to add more keywords:

```python
KENYAN_KEYWORDS = [
    "Your keyword",
    "Another keyword",
]
```

### Kenyan Locations

Edit `backend/kenyan_sources_config.py` to add more locations:

```python
KENYAN_LOCATIONS = [
    "Your Location",
    "Another Location",
]
```

## How It Works

### 1. Source-Based Scraping

Scrapes posts from configured accounts:
- Global sources: BBC, CNN, Reuters
- Kenyan sources: Nation, Standard, Tuko

**Frequency**: Every 15-30 minutes (configurable per source)

### 2. Hashtag-Based Scraping

Scrapes posts containing tracked hashtags:
- #KenyaElections
- #Nairobi
- #Mombasa
- #TrendingKenya
- etc.

**Frequency**: Every 30 minutes

### 3. Location Filtering

When available, extracts location/geotag data:
- Filters by Kenyan locations
- Boosts score for Kenyan content
- Shows location in dashboard

### 4. Engagement Filtering

Only high-engagement content is kept:
- Calculates engagement velocity
- Filters by minimum thresholds
- Low-engagement posts are discarded

### 5. Scoring & Prioritization

Stories are scored and prioritized:
- **50%** Engagement velocity
- **30%** Source credibility
- **20%** Topic relevance
- **Bonus** Kenyan content boost (+20 points)
- **Bonus** Kenyan location boost (+15 points)

**Result**: Kenyan stories appear first, sorted by score

## Data Structure

### Raw Posts

Each post includes:
- Platform, author, content
- Engagement metrics (likes, comments, shares, views)
- Location/geotag (if available)
- `is_kenyan` flag
- Media URL
- Posted timestamp

### Stories

Scored stories include:
- Overall score (0-100)
- Engagement velocity
- Topic (Politics, Entertainment, Sports, Tech)
- Location
- `is_kenyan` flag
- Reason flagged

## API Endpoints

### Get Stories (with Kenyan filters)

```bash
# All stories
GET /api/stories

# Only Kenyan stories
GET /api/stories?is_kenyan=true

# Stories from Nairobi
GET /api/stories?location=Nairobi

# Politics stories
GET /api/stories?topic=Politics

# Kenyan politics stories
GET /api/stories?is_kenyan=true&topic=Politics
```

### Get Hashtags

```bash
GET /api/hashtags
```

## Dashboard Display

Stories are displayed with:
- **Priority**: Kenyan stories first
- **Sorting**: By score (highest first)
- **Filtering**: By platform, location, topic
- **Tags**: Kenyan flag, location badge, topic badge

## Monitoring

### Check Scraping Activity

```sql
SELECT 
    scrape_type,
    status,
    posts_fetched,
    stories_created,
    started_at
FROM scrape_logs
ORDER BY started_at DESC
LIMIT 10;
```

### Check Kenyan Content

```sql
SELECT 
    platform,
    COUNT(*) as count,
    AVG(score) as avg_score,
    AVG(engagement_velocity) as avg_velocity
FROM stories
WHERE is_kenyan = true
GROUP BY platform;
```

### Check Hashtag Performance

```sql
SELECT 
    h.hashtag,
    COUNT(rp.id) as posts_count,
    COUNT(s.id) as stories_count
FROM hashtags h
LEFT JOIN raw_posts rp ON rp.hashtag_id = h.id
LEFT JOIN stories s ON s.raw_post_id = rp.id
GROUP BY h.id, h.hashtag;
```

## Troubleshooting

### No Kenyan Stories Showing

1. **Check sources are active:**
   ```sql
   SELECT * FROM sources WHERE is_kenyan = true AND is_active = true;
   ```

2. **Check scraping ran:**
   ```sql
   SELECT * FROM scrape_logs WHERE scrape_type = 'source' ORDER BY started_at DESC LIMIT 5;
   ```

3. **Check stories exist:**
   ```sql
   SELECT COUNT(*) FROM stories WHERE is_kenyan = true;
   ```

### Hashtag Scraping Not Working

- Twitter hashtag search requires API v2 access
- Instagram hashtag search requires Business Account
- Facebook hashtag search is limited
- TikTok hashtag search not directly supported

**Solution**: Focus on source-based scraping for now, hashtag support will improve with API access.

### Low Engagement Stories

Adjust thresholds in `.env`:
```env
MIN_ENGAGEMENT_SCORE=50
MIN_ENGAGEMENT_VELOCITY=10
```

## Adding New Kenyan Sources

1. **Edit `kenyan_sources_config.py`:**
   ```python
   KENYAN_SOURCES.append(
       SourceConfig(
           platform="X",
           account_handle="@NewAccount",
           account_name="New Account",
           is_kenyan=True,
           location="Nairobi"
       )
   )
   ```

2. **Reinitialize:**
   ```bash
   python init_kenyan_sources.py
   ```

3. **Update account ID** (for Facebook/Instagram)

4. **Test:**
   ```bash
   python trigger_scrape.py
   ```

## Best Practices

1. **Start with trusted sources** (Nation, Standard, Tuko)
2. **Monitor engagement thresholds** - adjust based on data
3. **Prioritize Kenyan content** - it's already configured
4. **Track key hashtags** - elections, major events
5. **Monitor scraping logs** - catch errors early

## Next Steps

1. ✅ Initialize Kenyan sources: `python init_kenyan_sources.py`
2. ✅ Update Facebook/Instagram IDs
3. ✅ Test scraping: `python trigger_scrape.py`
4. ✅ Start services (API, Celery)
5. ✅ Check dashboard for Kenyan stories!

Your system is now configured to prioritize Kenyan content while maintaining global context! 🇰🇪
