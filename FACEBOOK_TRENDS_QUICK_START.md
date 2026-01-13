# Facebook Trends - Quick Start Guide

## ✅ What Changed

**CRITICAL FIX:** System now uses **Page-based aggregation** instead of user profiles.

### Before (Broken)
- ❌ Tried to scrape from user profiles
- ❌ Empty results
- ❌ No trending content

### After (Fixed)
- ✅ Aggregates from multiple Facebook Pages
- ✅ Computes trends via `trend_score = (likes + comments + shares) / minutes_since_posted`
- ✅ Ranks and filters top trending posts
- ✅ Real trending stories

## 🚀 Quick Start (3 Steps)

### Step 1: Add Facebook Pages

```bash
cd backend
python add_facebook_pages.py
```

This will:
- Add predefined Kenyan media pages (Citizen TV, NTV, Nation, TUKO)
- Add global media pages (BBC News, CNN)
- Prompt for Page IDs if needed

**To get Page IDs:**
1. Go to: https://developers.facebook.com/tools/explorer/
2. Query: `GET /{page_username}` or search `GET /search?q={page_name}&type=page`
3. Copy the `id` field

### Step 2: Scrape Facebook Trends

```bash
python scrape_facebook_trends.py
```

This will:
- Aggregate posts from all active Facebook Pages
- Compute trend scores
- Store top 50 trending posts

### Step 3: Process to Stories

```bash
python process_posts_to_stories.py
```

This converts `raw_posts` to `stories` with proper scoring.

## 📊 How It Works

### Trend Computation

```
trend_score = (likes + comments + shares) / minutes_since_posted
```

**Example:**
- Post has 1000 likes, 100 comments, 50 shares
- Posted 30 minutes ago
- `trend_score = (1000 + 100 + 50) / 30 = 38.33 engagement/min`

### Ranking

1. Fetch posts from all Facebook Pages
2. Calculate `trend_score` for each
3. Sort by `trend_score DESC`
4. Keep top N (default: 50)
5. Filter by minimum `trend_score` (default: 10.0)

## 🎯 API Endpoint

You can also trigger via API:

```bash
curl -X POST "http://localhost:8000/api/scrape/facebook-trends?posts_per_page=10&top_n=50&min_trend_score=10.0"
```

## 🔄 Automatic Scraping

Celery Beat automatically:
1. Aggregates Facebook trends every 15 minutes
2. Scrapes other platforms (TikTok, etc.)
3. Processes posts to stories

## 📝 What You'll Get

**Database:**
- `raw_posts`: Aggregated posts from all Pages
- `stories`: Scored, filtered trending stories
- `reason_flagged`: "High engagement velocity"

**Dashboard:**
- Real trending stories from multiple sources
- Ranked by engagement velocity
- Ready for media company use

## ⚠️ Important Notes

1. **Only Facebook Pages** (not user profiles)
   - Pages have public posts
   - User profiles often empty/private

2. **Multiple Pages Required**
   - Single page = limited content
   - Multiple pages = real trends

3. **Trend Score Threshold**
   - Default: 10.0 engagement/min
   - Adjust based on your needs

## 🎉 Summary

**System now:**
- ✅ Aggregates from multiple Facebook Pages
- ✅ Computes trends via engagement velocity
- ✅ Ranks and filters top trending posts
- ✅ Shows real trending stories in dashboard

**This is how real media monitoring platforms work!**

See `backend/FACEBOOK_TRENDS_STRATEGY.md` for complete details.
