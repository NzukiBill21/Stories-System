# Focus on Facebook & TikTok - Setup Guide

## Current Plan

✅ **Facebook** - Ready to scrape  
✅ **TikTok** - Configured, ready to test  
⏸️ **Twitter** - Skipped for now  
⏸️ **Instagram** - Skipped for now  

## Quick Setup

### Step 1: Configure Sources

```bash
cd backend
python focus_facebook_tiktok.py
```

This will:
- ✅ Enable Facebook sources
- ✅ Enable TikTok sources
- ❌ Disable Twitter sources
- ❌ Disable Instagram sources

### Step 2: Verify Facebook Token

Make sure your Facebook token is in `.env`:

```env
FACEBOOK_ACCESS_TOKEN=your_facebook_token_here
```

Your Facebook page is already configured:
- **Page ID**: 1412325813805867
- **Page Name**: Bee Bill

### Step 3: Test Facebook

```bash
python test_facebook_instagram.py
```

Should show Facebook working!

### Step 4: Test TikTok

```bash
python test_tiktok_scraper.py
```

This will test if TikTok scraping works.

### Step 5: Start Scraping

```bash
# Manual scrape
python trigger_scrape.py

# Or automatic (requires Celery)
celery -A celery_app worker --loglevel=info  # Terminal 1
celery -A celery_app beat --loglevel=info    # Terminal 2
```

## What Will Be Scraped

### Facebook
- Posts from "Bee Bill" page (ID: 1412325813805867)
- Engagement metrics (likes, comments, shares)
- High-engagement content only
- Saved to database
- Appears on dashboard

### TikTok
- Trending videos
- High-engagement videos only (filtered)
- Engagement velocity calculated
- Saved to database
- Appears on dashboard

## Expected Results

After running `python trigger_scrape.py`:

1. **Facebook posts** fetched and saved
2. **TikTok videos** fetched and saved (if TikTokApi works)
3. **Stories created** from high-engagement content
4. **Dashboard shows** Facebook and TikTok stories

## Troubleshooting

### Facebook Not Working

1. **Check token:**
   ```bash
   python fix_facebook_token.py
   ```

2. **Check page ID:**
   - Should be: 1412325813805867
   - Verify in database

3. **Test manually:**
   ```python
   from platforms.facebook import FacebookScraper
   from models import Source
   
   source = Source(platform="Facebook", account_id="1412325813805867")
   scraper = FacebookScraper()
   posts = scraper.fetch_posts(source, limit=5)
   print(f"Fetched {len(posts)} posts")
   ```

### TikTok Not Working

1. **Check TikTokApi installed:**
   ```bash
   pip install TikTokApi playwright
   python -m playwright install chromium
   ```

2. **Test scraper:**
   ```bash
   python test_tiktok_scraper.py
   ```

3. **Check logs** for errors

## Monitoring

### Check What's Being Scraped

```sql
SELECT platform, COUNT(*) as count 
FROM raw_posts 
GROUP BY platform;
```

### Check Stories Created

```sql
SELECT platform, COUNT(*) as count, AVG(score) as avg_score
FROM stories
WHERE is_active = true
GROUP BY platform;
```

## Next Steps

1. ✅ Run `python focus_facebook_tiktok.py`
2. ✅ Test Facebook: `python test_facebook_instagram.py`
3. ✅ Test TikTok: `python test_tiktok_scraper.py`
4. ✅ Trigger scrape: `python trigger_scrape.py`
5. ✅ Check dashboard for stories!

## Summary

**Focus:** Facebook + TikTok  
**Status:** Ready to test  
**Action:** Run the focus script and start scraping!

Your dashboard will show Facebook and TikTok content! 🎉
