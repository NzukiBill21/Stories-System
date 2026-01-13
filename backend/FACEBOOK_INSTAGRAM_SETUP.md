# Facebook & Instagram Setup Guide

## Current Status

✅ **Tokens are configured** in your `.env` file  
⚠️ **Need to get Page/Account IDs** to fetch data

## The Issue

Facebook and Instagram Graph API require **numeric IDs**, not just handles/usernames.

- ❌ `account_handle="BBCNews"` - Won't work
- ✅ `account_id="123456789"` - This works!

## Step 1: Get Facebook Page ID

### Method 1: Graph API Explorer (Easiest)

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app (or create one)
3. Paste your access token
4. Query: `GET /me/accounts`
5. This shows all pages you manage with their IDs

### Method 2: Using Page Name

1. Go to: https://developers.facebook.com/tools/explorer/
2. Use your access token
3. Query: `GET /BBCNews?fields=id`
4. Returns: `{"id": "123456789"}`

### Method 3: From Page URL

1. Go to your Facebook page
2. Click "About" section
3. Scroll to find "Page ID" (numeric)

## Step 2: Get Instagram Account ID

### Method 1: Graph API Explorer

1. Go to: https://developers.facebook.com/tools/explorer/
2. Use your **Instagram** access token
3. Query: `GET /me?fields=id`
4. Returns your Instagram account ID

### Method 2: Using Username

1. Go to: https://developers.facebook.com/tools/explorer/
2. Use your Instagram access token
3. Query: `GET /{username}?fields=id`
   - Example: `GET /bbcnews?fields=id`
4. Returns: `{"id": "123456789"}`

## Step 3: Update Database

Once you have the IDs, update your sources:

```python
from database import SessionLocal
from models import Source

db = SessionLocal()

# Update Facebook source
fb_source = db.query(Source).filter(Source.platform == "Facebook").first()
if fb_source:
    fb_source.account_id = "123456789"  # Your Facebook page ID
    fb_source.account_handle = "BBCNews"  # Keep handle for display

# Update Instagram source
ig_source = db.query(Source).filter(Source.platform == "Instagram").first()
if ig_source:
    ig_source.account_id = "987654321"  # Your Instagram account ID
    ig_source.account_handle = "bbcnews"  # Keep handle for display

db.commit()
db.close()
```

## Step 4: Test

```bash
python test_facebook_instagram.py
```

This will:
- ✅ Check tokens are configured
- ✅ Test fetching posts
- ✅ Show sample data

## Step 5: Fetch Data

```bash
python trigger_scrape.py
```

This will fetch posts from Facebook and Instagram and save them to your database.

## What Gets Fetched

### Facebook
- Post text/message
- Likes count
- Comments count
- Shares count
- Post URL
- Timestamp

### Instagram
- Post caption
- Likes count
- Comments count
- Post URL
- Timestamp

## Troubleshooting

### "No posts fetched"

**Facebook:**
- Check page ID is correct (numeric, not handle)
- Verify token has `pages_read_engagement` permission
- Check page is public or you have admin access

**Instagram:**
- Check account ID is correct (numeric, not username)
- Verify token has `instagram_basic` permission
- Check account is public or you have access

### "Invalid access token"

- Token may have expired
- Regenerate token in Facebook Developer Console
- Update `.env` file with new token

### "Permission denied"

- Token needs specific permissions:
  - Facebook: `pages_read_engagement`, `pages_show_list`
  - Instagram: `instagram_basic`, `instagram_content_publish`

## Quick Test

Run this to see what's happening:

```bash
python test_facebook_instagram.py
```

It will show:
- ✅ If tokens are configured
- ✅ If IDs are needed
- ✅ If scraping works
- ✅ Sample data fetched

## Expected Flow

```
1. Configure tokens in .env ✅ (Done)
2. Get page/account IDs ⚠️ (Need to do)
3. Update database with IDs ⚠️ (Need to do)
4. Test scrapers ✅ (Run test script)
5. Fetch data ✅ (Run trigger_scrape.py)
6. View on dashboard ✅ (Stories appear!)
```

## Next Steps

1. **Get IDs** from Graph API Explorer
2. **Update database** with IDs
3. **Test** with `python test_facebook_instagram.py`
4. **Fetch data** with `python trigger_scrape.py`
5. **Check dashboard** - stories should appear!

Your tokens are ready, you just need to get the page/account IDs and update the database! 🚀
