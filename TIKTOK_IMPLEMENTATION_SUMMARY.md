# TikTok Scraper Implementation Summary

## ✅ What Was Created

### 1. TikTok Scraper (`backend/platforms/tiktok.py`)
- ✅ Full implementation using TikTokApi library
- ✅ Fetches trending TikTok videos
- ✅ Calculates engagement velocity: `(likes + comments + shares) / minutes_since_posted`
- ✅ Filters high-engagement content only
- ✅ Matches existing MySQL schema
- ✅ Comprehensive error handling
- ✅ Detailed logging

### 2. Configuration Updates
- ✅ Added TikTok config to `config.py`
- ✅ Updated `env.example` with Facebook and Instagram tokens
- ✅ Added TikTok settings: `TIKTOK_TRENDING_LIMIT`, `TIKTOK_MIN_ENGAGEMENT_VELOCITY`

### 3. Dependencies
- ✅ Added `TikTokApi==6.1.0` to `requirements.txt`
- ✅ Uses existing `playwright` (already in requirements)

### 4. Integration
- ✅ Registered in `platforms/__init__.py`
- ✅ Added TikTok source to `init_db.py`
- ✅ Works with existing scoring system
- ✅ Compatible with existing API endpoints

### 5. Testing & Documentation
- ✅ `test_tiktok_scraper.py` - Test script
- ✅ `TIKTOK_SETUP.md` - Complete setup guide
- ✅ `TIKTOK_QUICK_START.md` - Quick reference

## 🎯 Key Features

### Engagement Velocity Calculation
```python
velocity = (likes + comments + shares) / minutes_since_posted
```

**Example:**
- Video posted 10 minutes ago
- 5,000 likes + 500 comments + 200 shares = 5,700 engagement
- Velocity = 5,700 / 10 = **570 engagement/minute** ✅

### High-Engagement Filtering
- Only videos with `velocity >= TIKTOK_MIN_ENGAGEMENT_VELOCITY` are kept
- Low-engagement videos are filtered out **before** database insertion
- Configurable threshold in `.env`

### MySQL Schema Compatibility
Data is structured to match existing tables:

**raw_posts:**
- `platform_post_id` - TikTok video ID
- `platform` - "TikTok"
- `content` - Video caption
- `url` - TikTok video URL
- `posted_at` - Video creation timestamp
- `likes`, `comments`, `shares`, `views` - Engagement metrics
- `raw_data` - JSON string of raw TikTok data

**stories:**
- Automatically created from raw_posts
- `score` - Calculated by existing scoring system
- `engagement_velocity` - Engagement per minute
- `reason_flagged` - Why it was flagged

## 📋 Setup Steps

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt

# On Windows:
python -m playwright install chromium

# On Linux/Mac:
playwright install chromium
```

### 2. Configure Environment
Edit `backend/.env`:
```env
FACEBOOK_ACCESS_TOKEN=EAATni7kysWYBQXKTdOWV1Au5uc8yOaBNlAH2IH9LnxJCz8n1QXvZAQTg1rp8qkFQNc02o1EEvcnY7HoLF9M3QERtrdebkyTzY0yHA1oRM14OrbZCN0UwzZCcKI6XW9795Sl7mnvvZAagGiiz7JitRACEJBOQgF7xrOdSB0pzXYMgAuNPyhiupsU8eKlKibekFQCcrtDpTiL964ADJ7DZBm5YbeE9ZCOj7MatOVW2PkggwnYgF7FP6S1p92s55H6oDPxGShY3RWGoJtDrehWRxU

INSTAGRAM_ACCESS_TOKEN=EAATni7kysWYBQQVH4PIFaCNxaic5HKtJirpw9ZBflZCafiL74ZCHngDS00ZAbKpynDxvbapQUyhsQrvM9sz6LE7uLl8SMh56jV6rbookDCoSOTzXb5YYzliqazmdrZC8Q8d8BwfjekUjBla8sCVnuK45qRPdwwI4Xv9EGMDn3oC5vt4WCHCxthPZASUsgpd6kxAVOLPpZARUws4JEGZBNDsc507rQfZC4oY29lgZDZD

TIKTOK_TRENDING_LIMIT=50
TIKTOK_MIN_ENGAGEMENT_VELOCITY=100
```

### 3. Test the Scraper
```bash
python test_tiktok_scraper.py
```

### 4. Initialize Database (if not done)
```bash
python init_db.py
```

This adds a TikTok source automatically.

### 5. Trigger Scraping
```bash
python trigger_scrape.py
```

Or wait for automatic scraping via Celery.

## 🔄 Data Flow

```
1. TikTok Scraper
   ↓ (fetches trending videos)
2. Calculate Engagement Velocity
   ↓ (filters high-engagement only)
3. Save to raw_posts table
   ↓
4. Scoring System
   ↓ (calculates overall score)
5. Save to stories table
   ↓
6. API Endpoint
   ↓ (returns sorted by score)
7. Frontend Dashboard
   ↓ (displays TikTok stories)
```

## 📊 Configuration Options

### Trending Limit
```env
TIKTOK_TRENDING_LIMIT=50  # Number of videos to fetch per run
```

### Engagement Threshold
```env
TIKTOK_MIN_ENGAGEMENT_VELOCITY=100  # Minimum engagement per minute
```

**Adjust based on needs:**
- **Lower (50)**: More videos kept, less strict
- **Higher (200)**: Only very high-engagement videos

### Scraping Frequency
Edit source in database:
```python
source.scrape_frequency_minutes = 30  # Scrape every 30 minutes
```

## 🧪 Testing

### Test Scraper
```bash
python test_tiktok_scraper.py
```

### Verify Data Flow
```bash
python verify_data_flow.py
```

### Check TikTok Stories
```sql
SELECT platform, COUNT(*) as count, AVG(score) as avg_score
FROM stories
WHERE platform = 'TikTok'
GROUP BY platform;
```

## 📝 Logging

The scraper logs:
- Number of videos fetched
- Number passing filter
- Engagement velocity for each video
- Errors and warnings

**Example:**
```
INFO: Fetching 50 trending TikTok videos...
INFO: Fetched 50 videos, 12 passed engagement filter
DEBUG: Video 7123456789012345678 passed filter (velocity: 450.5)
DEBUG: Video 7123456789012345679 filtered out (velocity: 8.2 < 100)
```

## ⚠️ Important Notes

1. **TikTok Scraping**: Fetches **trending videos**, not user-specific content
2. **Velocity Unit**: Engagement per **minute** (not per hour like other platforms)
3. **Filtering**: Happens **before** database insertion (only high-engagement saved)
4. **Playwright Required**: Must install Chromium browser for TikTokApi
5. **Rate Limiting**: TikTok may rate limit - scraper handles gracefully

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Configure `.env` with tokens
3. ✅ Test scraper: `python test_tiktok_scraper.py`
4. ✅ Initialize database: `python init_db.py`
5. ✅ Trigger scraping: `python trigger_scrape.py`
6. ✅ Verify in dashboard: `http://localhost:5173`

## 📚 Documentation

- **Complete Guide**: `backend/TIKTOK_SETUP.md`
- **Quick Start**: `backend/TIKTOK_QUICK_START.md`
- **Test Script**: `backend/test_tiktok_scraper.py`

## ✅ Integration Status

- ✅ Modular design (inherits from `PlatformScraper`)
- ✅ MySQL-ready (matches existing schema)
- ✅ Error handling (graceful failures)
- ✅ Logging (comprehensive)
- ✅ Configurable (via `.env`)
- ✅ High-engagement only (filtered)
- ✅ Velocity calculation (per minute)
- ✅ Compatible with existing system

The TikTok scraper is **ready to use** and fully integrated with your Story Intelligence Dashboard! 🎉
