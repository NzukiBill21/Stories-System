# TikTok Scraper Setup Guide

## Overview

The TikTok scraper uses the `TikTokApi` library to fetch trending videos, calculate engagement velocity, and filter for high-engagement content only.

## Installation

### Step 1: Install Dependencies

```bash
cd backend
pip install TikTokApi playwright
```

### Step 2: Install Playwright Browser

TikTokApi requires Playwright to run:

**On Windows (PowerShell/CMD):**
```bash
python -m playwright install chromium
```

**On Linux/Mac:**
```bash
playwright install chromium
```

This downloads the Chromium browser needed for scraping (~122 MB).

### Step 3: Verify Installation

```python
from TikTokApi import TikTokApi
print("TikTokApi installed successfully")
```

## Configuration

### Environment Variables

Add to `backend/.env`:

```env
# TikTok Configuration
TIKTOK_TRENDING_LIMIT=50  # Number of trending videos to fetch per run
TIKTOK_MIN_ENGAGEMENT_VELOCITY=100  # Minimum engagement per minute to consider trending
```

### Understanding Engagement Velocity

**Formula:** `velocity = (likes + comments + shares) / minutes_since_posted`

- **High velocity** = Rapid engagement (trending content)
- **Low velocity** = Slow engagement (filtered out)

**Example:**
- Video posted 10 minutes ago
- 5,000 likes + 500 comments + 200 shares = 5,700 total engagement
- Velocity = 5,700 / 10 = 570 engagement/minute ✅ (kept)

- Video posted 2 hours ago
- 1,000 likes + 50 comments + 10 shares = 1,060 total engagement
- Velocity = 1,060 / 120 = 8.8 engagement/minute ❌ (filtered out)

## Usage

### Adding TikTok Source

The TikTok scraper fetches **trending videos** (not user-specific):

```python
from database import SessionLocal
from models import Source

db = SessionLocal()
tiktok_source = Source(
    platform="TikTok",
    account_handle="trending",  # Special handle for trending
    account_name="TikTok Trending",
    is_active=True,
    is_trusted=False,
    scrape_frequency_minutes=15
)
db.add(tiktok_source)
db.commit()
```

### Manual Scraping

```bash
python trigger_scrape.py
# Select TikTok source when prompted
```

### Automatic Scraping

TikTok scraping runs automatically via Celery every 15 minutes (or as configured).

## How It Works

### 1. Fetch Trending Videos

```python
scraper = TikTokScraper()
videos = scraper.fetch_posts(source, limit=50)
```

### 2. Calculate Engagement Velocity

For each video:
- Extract: likes, comments, shares, posted_at
- Calculate: `(likes + comments + shares) / minutes_since_posted`
- Compare to threshold: `TIKTOK_MIN_ENGAGEMENT_VELOCITY`

### 3. Filter High-Engagement Only

Only videos with velocity >= threshold are kept:
- ✅ High-engagement videos → Saved to database
- ❌ Low-engagement videos → Filtered out

### 4. Save to Database

Videos are saved to:
- `raw_posts` table (raw TikTok data)
- `stories` table (scored and normalized)

## Data Structure

### Raw Post (raw_posts table)

```python
{
    'platform_post_id': '7123456789012345678',  # TikTok video ID
    'platform': 'TikTok',
    'author': 'username',
    'content': 'Video caption...',
    'url': 'https://www.tiktok.com/@user/video/7123456789012345678',
    'posted_at': datetime(2024, 1, 9, 10, 30, 0),
    'likes': 50000,
    'comments': 5000,
    'shares': 2000,
    'views': 1000000,
    'raw_data': '{"id": "...", "stats": {...}, ...}'  # JSON string
}
```

### Story (stories table)

After scoring:
- `score`: Overall score (0-100)
- `engagement_velocity`: Engagement per minute
- `reason_flagged`: Why it was flagged (e.g., "High engagement velocity")
- `is_active`: True (if meets thresholds)

## Logging

The scraper logs:
- Number of videos fetched
- Number of videos passing filter
- Engagement velocity for each video
- Errors and warnings

**Example log output:**
```
INFO: Fetching 50 trending TikTok videos...
INFO: Fetched 50 videos, 12 passed engagement filter
DEBUG: Video 7123456789012345678 passed filter (velocity: 450.5)
DEBUG: Video 7123456789012345679 filtered out (velocity: 8.2 < 100)
```

## Troubleshooting

### "TikTokApi not installed"

```bash
pip install TikTokApi playwright
playwright install chromium
```

### "No videos fetched"

1. Check internet connection
2. TikTok may be blocking requests (try later)
3. Check TikTokApi library version compatibility

### "All videos filtered out"

- Lower `TIKTOK_MIN_ENGAGEMENT_VELOCITY` threshold
- Check if videos are actually trending
- Verify timestamp calculation is correct

### "Rate limit errors"

- TikTok may be rate limiting
- Increase `RATE_LIMIT_DELAY` in config
- Wait before retrying

### "Playwright browser not found"

**On Windows:**
```bash
python -m playwright install chromium
```

**On Linux/Mac:**
```bash
playwright install chromium
```

## Configuration Options

### Adjust Trending Limit

```env
TIKTOK_TRENDING_LIMIT=100  # Fetch more videos
```

### Adjust Engagement Threshold

```env
TIKTOK_MIN_ENGAGEMENT_VELOCITY=50  # Lower threshold (more videos kept)
TIKTOK_MIN_ENGAGEMENT_VELOCITY=200  # Higher threshold (only very high engagement)
```

### Adjust Scraping Frequency

Edit source in database:
```python
source.scrape_frequency_minutes = 30  # Scrape every 30 minutes
```

## Performance

- **Fetch time**: ~10-30 seconds for 50 videos
- **Filtering**: Instant (in-memory)
- **Database insert**: ~1-2 seconds per video
- **Total**: ~1-2 minutes per scrape run

## Best Practices

1. **Start with lower threshold** to see what's being filtered
2. **Monitor logs** to understand engagement patterns
3. **Adjust threshold** based on your needs
4. **Don't scrape too frequently** (TikTok may rate limit)
5. **Use trending videos** (not user-specific) for best results

## Integration with Existing System

The TikTok scraper:
- ✅ Uses same `PlatformScraper` base class
- ✅ Returns data in same format as other platforms
- ✅ Integrates with existing scoring system
- ✅ Saves to same MySQL tables
- ✅ Works with existing API endpoints
- ✅ Appears in dashboard like other platforms

## Verification

Test the scraper:

```python
from platforms.tiktok import TikTokScraper
from models import Source

scraper = TikTokScraper()
source = Source(platform="TikTok", account_handle="trending")
videos = scraper.fetch_posts(source, limit=10)
print(f"Fetched {len(videos)} videos")
```

Run full verification:

```bash
python verify_data_flow.py
```

Check TikTok-specific data:

```sql
SELECT platform, COUNT(*) as count, AVG(engagement_velocity) as avg_velocity
FROM stories
WHERE platform = 'TikTok'
GROUP BY platform;
```

## Notes

- TikTok scraping uses **trending videos**, not user-specific content
- Engagement velocity is calculated **per minute** (not per hour like other platforms)
- Videos are filtered **before** saving to database (only high-engagement kept)
- TikTokApi may require periodic updates if TikTok changes their API
