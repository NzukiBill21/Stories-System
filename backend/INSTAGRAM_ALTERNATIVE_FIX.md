# Instagram Alternative Fix - No "instagram_basic" Permission

## The Problem

- Changed to User Access Token ✅
- Still getting error ❌
- Don't see "instagram_basic" permission ❌

**Cause:** Your app doesn't have Instagram product configured

## Solution Options

### Option 1: Add Instagram Product to App (Recommended)

1. **Go to Facebook Apps:**
   https://developers.facebook.com/apps/

2. **Select your app** ("Stories" or whatever it's called)

3. **Add Instagram Product:**
   - Click "Add Product" or "+" button
   - Find "Instagram Basic Display" or "Instagram Graph API"
   - Click "Set Up"

4. **Configure Instagram:**
   - Follow the setup wizard
   - Connect your Instagram account
   - Authorize the app

5. **Go back to Graph API Explorer:**
   - Refresh the page
   - Now you should see "instagram_basic" permission
   - Generate token with that permission

### Option 2: Use Facebook Page Token (Workaround)

If you have a Facebook Page connected to Instagram:

1. **In Graph API Explorer:**
   - Select your **Facebook Page** (not App Token, not User)
   - Query: `GET /me/accounts`
   - This shows all pages you manage

2. **Get Page Access Token:**
   - Find your page in the results
   - Copy the `access_token` from that page
   - This is your **Page Access Token**

3. **Get Instagram Business Account:**
   - Query: `GET /{page-id}?fields=instagram_business_account`
   - This gives you the Instagram Business Account ID

4. **Use Page Token for Instagram:**
   - The page token can access Instagram if page is connected
   - Use this token in `.env`

### Option 3: Skip Instagram for Now (Temporary)

If Instagram setup is too complex:

1. **Disable Instagram scraper temporarily:**
   ```python
   # In database, set Instagram source to inactive
   from database import SessionLocal
   from models import Source
   
   db = SessionLocal()
   ig = db.query(Source).filter(Source.platform == "Instagram").first()
   if ig:
       ig.is_active = False
       db.commit()
   ```

2. **Focus on Facebook and other platforms first**
3. **Add Instagram later** when app is configured

## Quick Test: Check What You Have

Run this to see what's available:

```python
import requests
from config import settings

# Test with current token
token = settings.instagram_access_token

# Try different endpoints
endpoints = [
    ("User Info", f"https://graph.instagram.com/v18.0/me?fields=id,username&access_token={token}"),
    ("Facebook User", f"https://graph.facebook.com/v18.0/me?access_token={token}"),
    ("Facebook Pages", f"https://graph.facebook.com/v18.0/me/accounts?access_token={token}"),
]

for name, url in endpoints:
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'error' not in data:
            print(f"✅ {name}: Works!")
            print(f"   {data}")
        else:
            print(f"❌ {name}: {data['error']['message']}")
    except Exception as e:
        print(f"❌ {name}: {e}")
```

## Recommended: Use Facebook Page Token

Since you have Facebook working, use the same approach:

1. **Get Facebook Page Token** (you already have page ID: 1412325813805867)
2. **Check if page has Instagram:**
   ```
   GET /1412325813805867?fields=instagram_business_account
   ```
3. **If yes, use the page token for Instagram scraping**

## Update Scraper to Handle This

The Instagram scraper will work with:
- Instagram User Token (if you have instagram_basic)
- Facebook Page Token (if page connected to Instagram)
- Or gracefully skip if neither works

## Next Steps

**Quick Fix (5 minutes):**
1. Go to https://developers.facebook.com/apps/
2. Select your app
3. Add "Instagram Basic Display" product
4. Configure it
5. Go back to Graph API Explorer
6. Now "instagram_basic" will appear
7. Generate token

**Or Use Facebook Page:**
1. Use your Facebook page token
2. Check if page has Instagram connected
3. Use that for scraping

**Or Skip for Now:**
1. Disable Instagram source
2. Use Facebook, Twitter, TikTok
3. Add Instagram later

Let me know which option you want to try!
