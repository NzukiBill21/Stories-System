# ✅ Kenyan Content Scraping - Ready to Use!

## 🎉 Implementation Complete

Your Python backend is now fully configured to pull high-engagement content from TikTok, Instagram, and Facebook with a focus on both global and local Kenyan trends!

## 📋 What's Been Implemented

### ✅ Global Sources
- BBC News (X)
- CNN (X)  
- Reuters (X)

### ✅ Kenyan Sources
- Nation Africa (X, Facebook, Instagram)
- Standard Digital (X)
- Tuko News (X)

### ✅ Kenyan Hashtags Tracked
- #KenyaElections
- #Nairobi
- #Mombasa
- #TrendingKenya
- #Kenya
- #KenyaNews
- #KenyaPolitics
- #NairobiTrending

### ✅ Features
- **High-engagement filtering** - Only trending content kept
- **Location filtering** - Kenyan locations prioritized
- **Hashtag tracking** - Dynamic hashtag monitoring
- **Topic classification** - Politics, Entertainment, Sports, Tech
- **Kenyan priority** - Kenyan stories appear first
- **Modular design** - Easy to add new sources/hashtags

## 🚀 Quick Start (3 Steps)

### Step 1: Initialize Kenyan Sources

```bash
cd backend
python init_kenyan_sources.py
```

This creates:
- ✅ Database tables (including `hashtags`)
- ✅ Global sources (BBC, CNN, Reuters)
- ✅ Kenyan sources (Nation, Standard, Tuko)
- ✅ Kenyan hashtags (#KenyaElections, #Nairobi, etc.)

### Step 2: Update Facebook/Instagram IDs

Get numeric IDs from Facebook Graph API Explorer, then:

```python
from database import SessionLocal
from models import Source

db = SessionLocal()
fb = db.query(Source).filter(Source.platform == "Facebook").first()
fb.account_id = "YOUR_FACEBOOK_PAGE_ID"
ig = db.query(Source).filter(Source.platform == "Instagram").first()
ig.account_id = "YOUR_INSTAGRAM_ACCOUNT_ID"
db.commit()
```

### Step 3: Start Scraping

```bash
# Trigger manual scrape
python trigger_scrape.py

# Or start automatic scraping
celery -A celery_app worker --loglevel=info  # Terminal 1
celery -A celery_app beat --loglevel=info    # Terminal 2
```

## 📊 What Gets Scraped

### Source-Based (Every 15 minutes)
- Posts from BBC, CNN, Reuters (global context)
- Posts from Nation, Standard, Tuko (Kenyan news)
- High-engagement posts only
- Location data when available

### Hashtag-Based (Every 30 minutes)
- Posts with #KenyaElections, #Nairobi, #Mombasa, etc.
- Cross-platform hashtag tracking
- High-engagement filtering
- Kenyan content prioritized

## 🎯 Dashboard Display

Stories are displayed with:
1. **Kenyan stories first** (priority)
2. **Sorted by score** (highest engagement)
3. **Location badges** (Nairobi, Mombasa, etc.)
4. **Topic tags** (Politics, Entertainment, Sports, Tech)
5. **High-engagement only** (low engagement filtered out)

## 🔧 Configuration

### Add More Sources

Edit `backend/kenyan_sources_config.py`:
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

Run: `python init_kenyan_sources.py`

### Add More Hashtags

Edit `backend/kenyan_sources_config.py`:
```python
KENYAN_HASHTAGS.append(
    HashtagConfig(
        hashtag="#NewHashtag",
        platform="all",
        is_kenyan=True,
        posts_per_hashtag=20
    )
)
```

### Adjust Engagement Thresholds

Edit `backend/.env`:
```env
MIN_ENGAGEMENT_SCORE=50
MIN_ENGAGEMENT_VELOCITY=10
```

## 📈 API Endpoints

### Get Stories
```bash
# All stories
GET /api/stories

# Only Kenyan stories
GET /api/stories?is_kenyan=true

# Stories from Nairobi
GET /api/stories?location=Nairobi

# Politics stories
GET /api/stories?topic=Politics

# Kenyan politics from Nairobi
GET /api/stories?is_kenyan=true&topic=Politics&location=Nairobi
```

### Get Sources
```bash
# All sources
GET /api/sources

# Only Kenyan sources
GET /api/sources?is_kenyan=true
```

### Get Hashtags
```bash
# All hashtags
GET /api/hashtags

# Only Kenyan hashtags
GET /api/hashtags?is_kenyan=true
```

### Trigger Hashtag Scraping
```bash
POST /api/scrape/hashtag/{hashtag_id}
```

## 📝 Data Structure

### Each Post Includes:
- ✅ Platform (X, Facebook, Instagram, TikTok)
- ✅ Author/account name
- ✅ Content text/caption
- ✅ Media URL (if available)
- ✅ Engagement metrics (likes, comments, shares, views)
- ✅ Posted timestamp
- ✅ URL to original content
- ✅ Location/geotag (when available)
- ✅ Kenyan flag (`is_kenyan`)
- ✅ Topic classification

### Scoring:
- **50%** Engagement velocity
- **30%** Source credibility
- **20%** Topic relevance
- **+20 points** Kenyan content boost
- **+15 points** Kenyan location boost

## 🎯 Expected Results

After running `python init_kenyan_sources.py` and `python trigger_scrape.py`:

1. ✅ Database populated with sources and hashtags
2. ✅ Posts fetched from Kenyan sources
3. ✅ Posts fetched by hashtags
4. ✅ High-engagement posts scored and saved
5. ✅ Stories appear on dashboard
6. ✅ Kenyan stories prioritized and sorted

## 📚 Documentation

- **Setup Guide**: `backend/KENYAN_SETUP_GUIDE.md`
- **Implementation Summary**: `backend/KENYAN_IMPLEMENTATION_SUMMARY.md`
- **Configuration**: `backend/kenyan_sources_config.py`

## ✅ Next Steps

1. **Initialize**: `python init_kenyan_sources.py`
2. **Update IDs**: Get Facebook/Instagram account IDs
3. **Test**: `python trigger_scrape.py`
4. **Start Services**: API + Celery worker + Celery beat
5. **View Dashboard**: Kenyan stories should appear!

## 🎉 You're All Set!

The system is configured to:
- ✅ Pull high-engagement content from TikTok, Instagram, Facebook
- ✅ Focus on global (BBC, CNN) and Kenyan (Nation, Standard, Tuko) sources
- ✅ Track Kenyan hashtags dynamically
- ✅ Filter by location when available
- ✅ Prioritize Kenyan content
- ✅ Filter high-engagement only
- ✅ Store in MySQL
- ✅ Display on dashboard with proper hierarchy

**Run `python init_kenyan_sources.py` to get started!** 🇰🇪
