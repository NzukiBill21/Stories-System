# Facebook Token Error Fix

## The Problem

You're getting this error:
```json
{
  "error": {
    "message": "Invalid OAuth access token - Cannot parse access token",
    "type": "OAuthException",
    "code": 190
  }
}
```

This means your Facebook access token is:
- ❌ Expired
- ❌ Invalid format
- ❌ Missing required permissions
- ❌ Revoked

## Solution: Get a New Access Token

### Method 1: Graph API Explorer (Easiest)

1. **Go to Graph API Explorer:**
   https://developers.facebook.com/tools/explorer/

2. **Select Your App:**
   - Click "Meta App" dropdown
   - Select your app (or create one if needed)

3. **Get User Token:**
   - Click "Generate Access Token"
   - Select permissions:
     - `pages_read_engagement`
     - `pages_show_list`
     - `pages_read_user_content`
   - Click "Generate Access Token"
   - **Copy the token** (starts with `EAAT...`)

4. **Get Page Access Token:**
   - Query: `GET /me/accounts`
   - This shows all pages you manage
   - Find your page (e.g., "Bee Bill")
   - Copy the `access_token` from that page object
   - **This is your page access token** (use this one!)

### Method 2: Long-Lived Token (Recommended for Production)

1. **Get Short-Lived Token** (from Method 1)

2. **Exchange for Long-Lived Token:**
   ```
   GET https://graph.facebook.com/v18.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id=YOUR_APP_ID&
     client_secret=YOUR_APP_SECRET&
     fb_exchange_token=SHORT_LIVED_TOKEN
   ```

3. **Use Long-Lived Token** (valid for 60 days)

### Method 3: Page Access Token (Best for Scraping)

1. **Get User Access Token** (from Method 1)

2. **Get Your Pages:**
   ```
   GET /me/accounts?access_token=USER_TOKEN
   ```

3. **Extract Page Access Token:**
   - Response includes `access_token` for each page
   - Use the page access token (not user token)
   - This token has page-specific permissions

## Update Your Configuration

### Step 1: Update .env File

Edit `backend/.env`:

```env
FACEBOOK_ACCESS_TOKEN=EAATni7kysWYBQ...your_new_token_here
```

### Step 2: Test the Token

```bash
cd backend
python test_facebook_instagram.py
```

Or test manually:

```python
import requests

token = "YOUR_NEW_TOKEN"
response = requests.get(
    f"https://graph.facebook.com/v18.0/me?access_token={token}"
)
print(response.json())
```

## Using Your Page ID

You found your page ID: `1412325813805867` (Bee Bill)

### Update Database

```python
from database import SessionLocal
from models import Source

db = SessionLocal()

# Update Facebook source with your page ID
fb_source = db.query(Source).filter(Source.platform == "Facebook").first()
if fb_source:
    fb_source.account_id = "1412325813805867"  # Your page ID
    fb_source.account_handle = "Bee Bill"  # Your page name
    db.commit()
    print("Facebook source updated!")
else:
    # Create new source
    fb_source = Source(
        platform="Facebook",
        account_handle="Bee Bill",
        account_name="Bee Bill",
        account_id="1412325813805867",
        is_active=True,
        is_kenyan=False  # Set to True if Kenyan content
    )
    db.add(fb_source)
    db.commit()
    print("Facebook source created!")

db.close()
```

## Test Facebook Scraper

```python
from database import SessionLocal
from models import Source
from platforms.facebook import FacebookScraper

db = SessionLocal()
source = db.query(Source).filter(Source.platform == "Facebook").first()

if source:
    scraper = FacebookScraper()
    posts = scraper.fetch_posts(source, limit=5)
    print(f"Fetched {len(posts)} posts")
    for post in posts:
        print(f"  - {post['content'][:50]}... ({post['likes']} likes)")
else:
    print("Facebook source not found")
```

## Common Issues

### "Token expired"
- Tokens expire after 1-2 hours (short-lived)
- Get a new token or exchange for long-lived token

### "Invalid permissions"
- Token needs `pages_read_engagement` permission
- Regenerate token with correct permissions

### "Page not found"
- Check page ID is correct
- Verify you have admin access to the page
- Use page access token (not user token)

### "Rate limit exceeded"
- Too many requests
- Wait and retry
- Use batch requests if possible

## Quick Fix Script

Create `backend/fix_facebook_token.py`:

```python
"""Quick script to test and update Facebook token."""
import requests
from config import settings

# Test current token
token = settings.facebook_access_token
if not token:
    print("No Facebook token configured")
    exit(1)

print(f"Testing token: {token[:20]}...")

# Test 1: Get user info
response = requests.get(
    f"https://graph.facebook.com/v18.0/me?access_token={token}"
)
print(f"\nUser info: {response.json()}")

# Test 2: Get pages
response = requests.get(
    f"https://graph.facebook.com/v18.0/me/accounts?access_token={token}"
)
data = response.json()

if 'error' in data:
    print(f"\n❌ Error: {data['error']['message']}")
    print("\nToken is invalid. Get a new one from:")
    print("https://developers.facebook.com/tools/explorer/")
else:
    print(f"\n✅ Token is valid!")
    print(f"Pages you manage: {len(data.get('data', []))}")
    for page in data.get('data', [])[:5]:
        print(f"  - {page['name']} (ID: {page['id']})")
        print(f"    Access Token: {page['access_token'][:20]}...")
        print(f"    Use this page token for scraping!")
```

Run it:
```bash
python fix_facebook_token.py
```

## Next Steps

1. **Get new token** from Graph API Explorer
2. **Update .env** with new token
3. **Update database** with page ID (1412325813805867)
4. **Test scraper** with `python test_facebook_instagram.py`
5. **Start scraping** with `python trigger_scrape.py`

## Important Notes

- **Page Access Token** is better than User Token for scraping
- **Long-lived tokens** last 60 days (vs 1-2 hours for short-lived)
- **Page ID** (1412325813805867) is what you use in API calls
- **Token permissions** must include `pages_read_engagement`

Your page ID is ready: `1412325813805867` - just need a valid token! 🔑
