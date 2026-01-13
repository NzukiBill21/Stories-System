# Quick Facebook Token Fix

## The Problem

Your Facebook token is **expired or invalid**. You're getting:
```
"Invalid OAuth access token - Cannot parse access token"
```

## Quick Solution (5 minutes)

### Step 1: Get New Token

1. Go to: **https://developers.facebook.com/tools/explorer/**
2. Click **"Generate Access Token"**
3. Select permissions:
   - ✅ `pages_read_engagement`
   - ✅ `pages_show_list`
4. Click **"Generate Access Token"**
5. **Copy the token** (starts with `EAAT...`)

### Step 2: Get Page Access Token (Better!)

After getting user token:

1. In Graph API Explorer, query: `GET /me/accounts`
2. Find your page "Bee Bill" (ID: 1412325813805867)
3. Copy the `access_token` from that page object
4. **Use this page token** (it's better for scraping!)

### Step 3: Update .env File

Create `backend/.env` file (copy from `env.example`):

```env
# Copy all from env.example, then update this line:
FACEBOOK_ACCESS_TOKEN=YOUR_NEW_TOKEN_HERE
```

### Step 4: Update Database with Your Page ID

You already have your page ID: `1412325813805867`

Run this Python script:

```python
from database import SessionLocal
from models import Source

db = SessionLocal()

# Update or create Facebook source
source = db.query(Source).filter(Source.platform == "Facebook").first()
if source:
    source.account_id = "1412325813805867"
    source.account_handle = "Bee Bill"
    source.account_name = "Bee Bill"
    print("Updated Facebook source!")
else:
    source = Source(
        platform="Facebook",
        account_handle="Bee Bill",
        account_name="Bee Bill",
        account_id="1412325813805867",
        is_active=True
    )
    db.add(source)
    print("Created Facebook source!")

db.commit()
db.close()
```

### Step 5: Test

```bash
python fix_facebook_token.py
```

Should show: `[OK] Token is valid!`

## Your Page Info

- **Page Name**: Bee Bill
- **Page ID**: 1412325813805867
- **Status**: Ready to use (just need valid token)

## Why Token Expired?

Facebook tokens expire:
- **User tokens**: 1-2 hours
- **Page tokens**: 1-2 hours (but can be extended)
- **Long-lived tokens**: 60 days

**Solution**: Get a new token or exchange for long-lived token.

## Get Long-Lived Token (Optional)

If you want a token that lasts 60 days:

```
GET https://graph.facebook.com/v18.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id=YOUR_APP_ID&
  client_secret=YOUR_APP_SECRET&
  fb_exchange_token=SHORT_LIVED_TOKEN
```

Replace:
- `YOUR_APP_ID` - From Facebook Developer Console
- `YOUR_APP_SECRET` - From Facebook Developer Console  
- `SHORT_LIVED_TOKEN` - The token you just got

## Test After Fix

```bash
# Test token
python fix_facebook_token.py

# Test scraper
python test_facebook_instagram.py

# Trigger scrape
python trigger_scrape.py
```

## Summary

1. ✅ Get new token from Graph API Explorer
2. ✅ Update `backend/.env` with new token
3. ✅ Update database with page ID (1412325813805867)
4. ✅ Test and start scraping!

Your page is ready - just need a fresh token! 🔑
