# How to Get Real Data - Complete Guide

## Current Situation

**What's Working:**
- ✅ System is configured
- ✅ Database connected
- ✅ API working
- ✅ Frontend showing data
- ✅ Stories have headlines
- ✅ Detail view should open

**What's Not Working:**
- ❌ Facebook user profile has no posts (empty/private)
- ❌ TikTok API needs configuration
- ❌ No real content being scraped yet

## Why No Real Data?

### Facebook
- "Bee Bill" is a **user profile**, not a **Page**
- User profiles often have no public posts
- Need Facebook **Pages** with public content

### TikTok
- TikTokApi needs proper setup
- May need session ID or different method

## Solution: Add Sources with Public Content

### Step 1: Add Facebook Pages

**Find Public Facebook Pages:**
- News organizations (BBC, CNN, Reuters)
- Public figures
- Companies with public pages

**Add to Database:**
```python
from database import SessionLocal
from models import Source

db = SessionLocal()

# Example: Add BBC News page
bbc = Source(
    platform="Facebook",
    account_handle="bbcnews",
    account_name="BBC News",
    account_id="228735667216",  # Get from Graph API Explorer
    is_active=True,
    is_trusted=True
)
db.add(bbc)
db.commit()
```

### Step 2: Get Page IDs

**Method 1: Graph API Explorer**
1. Go to: https://developers.facebook.com/tools/explorer/
2. Query: `GET /me/accounts` (if you manage pages)
3. Or search for page: `GET /search?q=BBC&type=page`

**Method 2: Find Page ID**
- Use: https://findmyfbid.com/
- Enter page URL
- Get page ID

### Step 3: Scrape Real Content

```bash
python scrape_and_verify.py
```

## What You'll Get

Once you add pages with public content:
- Real posts from Facebook Pages
- Real engagement metrics
- Real headlines
- Stories ready for media company

## Quick Test

Add a test page and scrape:

```python
# Quick script to add BBC News page
from database import SessionLocal
from models import Source

db = SessionLocal()
bbc = Source(
    platform="Facebook",
    account_handle="bbcnews",
    account_name="BBC News",
    account_id="228735667216",
    is_active=True,
    is_trusted=True
)
db.add(bbc)
db.commit()
print("BBC News page added!")
```

Then scrape:
```bash
python scrape_and_verify.py
```

## Summary

**System is Ready:**
- ✅ Everything configured
- ✅ Headlines working
- ✅ Detail view should work

**Need:**
- ⚠️ Sources with public content (Facebook Pages, not user profiles)
- ⚠️ Or fix TikTok scraping

**Your system will pull real data once you add sources with public content!** 🎉
