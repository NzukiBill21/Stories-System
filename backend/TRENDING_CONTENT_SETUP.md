# Trending Content Setup - Complete Guide

## ✅ What Was Fixed

### 1. Facebook User Profile Support ✅
- **Issue:** Facebook scraper only worked for Pages, not user profiles
- **Fix:** Updated scraper to try `/posts` (Pages) then `/feed` (user profiles)
- **Status:** Now works with user profiles like "Bee Bill"

### 2. TikTok Platform Added ✅
- **Issue:** TikTok wasn't showing as a platform option
- **Fix:** Created TikTok trending source in database
- **Status:** TikTok now appears as active source and platform option

### 3. Trending Content Focus ✅
- **Issue:** System was only scraping specific accounts
- **Fix:** Configured for trending content discovery
- **Status:** TikTok fetches trending videos, Facebook fetches user posts

## 📊 Current Configuration

### Active Sources

1. **TikTok - Trending Videos**
   - Fetches trending/high-engagement videos
   - Filters by engagement velocity
   - Only keeps videos with rapid engagement
   - Perfect for discovering trending news/stories

2. **Facebook - User Profile**
   - Fetches posts from "Bee Bill" user profile
   - Uses `/feed` endpoint for user profiles
   - Gets all posts with engagement metrics

## 🎯 How It Works

### TikTok Trending
- Scraper fetches trending videos from TikTok
- Calculates engagement velocity: `(likes + comments + shares) / minutes_since_posted`
- Only keeps videos above threshold (default: 100 engagement/min)
- Perfect for discovering viral content and trending topics

### Facebook User Profile
- Scraper fetches posts from user profile
- Gets posts with engagement metrics
- Processes and scores each post
- Creates stories for high-engagement content

## 🚀 Usage

### Start Scraping

```bash
cd backend
python trigger_scrape_now.py
```

Or test:
```bash
python test_trending_scraping.py
```

### View Results

1. **Start API:**
   ```bash
   python main.py
   ```

2. **Start Frontend:**
   ```bash
   npm run dev
   ```

3. **View Dashboard:**
   - Open: http://localhost:3000
   - Filter by platform: TikTok, Facebook
   - See trending stories sorted by engagement

### API Endpoints

```bash
# Get all stories
GET /api/stories

# Filter by platform
GET /api/stories?platform=TikTok
GET /api/stories?platform=Facebook

# Get sources (shows TikTok)
GET /api/sources
```

## 📈 What You'll Get

### From TikTok
- Trending videos with high engagement
- News stories going viral
- Entertainment content
- Filtered by engagement velocity
- Only high-impact content

### From Facebook
- Posts from user profile
- High-engagement posts
- News and trending topics
- Scored and ranked

## ✅ Platform Options

TikTok now appears as a platform option in:
- API: `/api/stories?platform=TikTok`
- Dashboard: Filter dropdown
- Sources: `/api/sources` shows TikTok source

## 🎯 Perfect for Media Company

This setup is ideal for:
- ✅ Discovering trending content
- ✅ Finding high-engagement stories
- ✅ Tracking viral news
- ✅ Filtering by engagement
- ✅ Getting content ready for publication

## Summary

**Fixed:**
- ✅ Facebook user profile support
- ✅ TikTok platform added and visible
- ✅ Trending content discovery configured

**Ready:**
- ✅ TikTok: Trending videos
- ✅ Facebook: User profile posts
- ✅ System: Scraping and showing data

**Your system is now configured for trending content discovery!** 🎉
