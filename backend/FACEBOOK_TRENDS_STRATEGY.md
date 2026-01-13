# Facebook Trends Strategy - Complete Implementation

## ✅ Critical Change Implemented

**STOP:** Attempting to fetch from user profiles or `/me/posts`  
**START:** Page-based aggregation with trend computation

## How It Works

### 1. Facebook: Page-Based Aggregation (NOT user profiles)

**Only fetch from public Facebook Pages:**
- Use Page IDs (not user profile IDs)
- Query: `GET /{page_id}/posts`
- Extract: `message`, `created_time`, `likes.summary(true)`, `comments.summary(true)`, `shares`, `permalink_url`

### 2. Simulate "Facebook Trends"

**Facebook has no trending endpoint. Trends must be computed:**

```
trend_score = (likes + comments + shares) / minutes_since_posted
```

**Process:**
1. Aggregate posts from many public Pages
2. Calculate `trend_score` for each post
3. Sort by `trend_score DESC`
4. Keep only top N (e.g., 20-50)

**This ranked output is the Facebook Trends feed.**

### 3. Source Strategy (Mandatory)

**Use multiple Pages, not one account:**
- ✅ Prioritize Kenyan media pages, then global reference pages
- ❌ Ignore personal profiles entirely

**Example valid sources:**
- Citizen TV Kenya
- NTV Kenya
- Nation Media
- TUKO
- BBC News
- CNN

### 4. Database Expectations

- Store raw data in `raw_posts`
- Store scored, filtered data in `stories`
- Mark `reason_flagged` as **"High engagement velocity"**

### 5. TikTok Handling (Different Logic)

- Use TikTokApi to pull:
  - Trending videos
  - Hashtag-based content
  - Region-relevant content
- Apply the same engagement-velocity scoring

### 6. Final Output

- Node.js UI reads from `stories` table
- Feed shows real trending stories, not account-specific posts

## Implementation Files

### Core Components

1. **`trend_aggregator.py`**
   - `calculate_trend_score()` - Computes trend score
   - `aggregate_facebook_trends()` - Aggregates from multiple Pages
   - `scrape_and_store_trends()` - Stores trending posts

2. **`platforms/facebook.py`** (Updated)
   - Only works with Facebook Pages (not user profiles)
   - Uses `/posts` endpoint only
   - Validates Page ID exists

3. **`services.py`** (Updated)
   - Imports `trend_aggregator`
   - Sets `reason_flagged = "High engagement velocity"` for Facebook

4. **`celery_app.py`** (Updated)
   - Separates Facebook Pages from other sources
   - Aggregates Facebook trends before scraping other platforms

### Scripts

1. **`add_facebook_pages.py`**
   - Adds public Facebook Pages to database
   - Includes Kenyan media and global reference pages
   - Prompts for Page IDs if not provided

2. **`scrape_facebook_trends.py`**
   - Aggregates trends from all active Facebook Pages
   - Computes trend scores
   - Stores top N trending posts

3. **`process_posts_to_stories.py`**
   - Processes raw posts to stories after aggregation
   - Converts `raw_posts` to `stories` with scoring

### API Endpoints

1. **`POST /api/scrape/facebook-trends`**
   - Triggers Facebook trend aggregation
   - Parameters: `posts_per_page`, `top_n`, `min_trend_score`
   - Returns: Summary statistics

## Usage

### Step 1: Add Facebook Pages

```bash
python add_facebook_pages.py
```

This will:
- Add predefined Kenyan media pages (need Page IDs)
- Add predefined global media pages
- Prompt for Page IDs if not provided

### Step 2: Scrape Facebook Trends

```bash
python scrape_facebook_trends.py
```

Or via API:
```bash
curl -X POST "http://localhost:8000/api/scrape/facebook-trends?posts_per_page=10&top_n=50&min_trend_score=10.0"
```

### Step 3: Process to Stories

```bash
python process_posts_to_stories.py
```

This converts `raw_posts` to `stories` with proper scoring.

### Step 4: View Dashboard

Stories will appear in the dashboard, showing real trending content.

## Automatic Scraping

Celery Beat automatically:
1. Aggregates Facebook trends from all Pages
2. Scrapes other platforms (TikTok, etc.)
3. Processes posts to stories

Runs every 15 minutes (configurable).

## What This Achieves

✅ **Fixes the "no real Facebook data" issue permanently**
- Uses Pages with public content
- Computes trends via aggregation

✅ **Aligns with real media monitoring platforms**
- Trend computation, not explicit trending API
- Multi-source aggregation

✅ **Defensible, scalable, newsroom-ready**
- Proper trend scoring
- Multiple source aggregation
- High-engagement filtering

✅ **Positions you as someone who understands data systems**
- Not just scraping
- Proper trend computation
- Scalable architecture

## Key Differences from Before

| Before | After |
|--------|-------|
| User profiles | Facebook Pages only |
| Single account | Multiple Pages aggregated |
| No trend computation | `trend_score = engagement / minutes` |
| Account-specific posts | Real trending stories |
| Empty results | Real trending content |

## Summary

**Facebook trends are emergent, not explicit.**

The system now:
1. ✅ Aggregates from multiple Facebook Pages
2. ✅ Computes trends via engagement velocity
3. ✅ Ranks and filters top trending posts
4. ✅ Stores in database with proper scoring
5. ✅ Shows real trending stories in dashboard

**This is how real media monitoring platforms work!** 🎉
