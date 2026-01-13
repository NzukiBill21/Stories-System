# Instagram Token Fix Guide

## The Problem

Instagram tokens can have several issues:
- Token expired (Instagram tokens expire after 60 days)
- Wrong token type (need Instagram token, not Facebook token)
- Missing permissions (`instagram_basic` required)
- Account ID not found

## Solution: Get Instagram Account ID

### Step 1: Get Instagram Access Token

1. **Go to Graph API Explorer:**
   https://developers.facebook.com/tools/explorer/

2. **Select Your App:**
   - Click "Meta App" dropdown
   - Select your app (must have Instagram Basic Display or Instagram Graph API)

3. **Generate Token:**
   - Click "Generate Access Token"
   - Select permissions:
     - ✅ `instagram_basic`
     - ✅ `instagram_content_publish` (if needed)
   - Click "Generate Access Token"
   - **Copy the token** (starts with `IG...` or `EAAT...`)

### Step 2: Get Instagram Account ID

**Method 1: Using /me endpoint**

1. In Graph API Explorer, query:
   ```
   GET /me?fields=id,username
   ```

2. Response should be:
   ```json
   {
     "id": "17841405309211844",
     "username": "your_username"
   }
   ```

3. **Copy the `id`** - this is your Instagram Account ID

**Method 2: Using Business Account (if you have one)**

1. Query:
   ```
   GET /me/accounts
   ```

2. Find your Instagram Business Account
3. Get the account ID from there

### Step 3: Test Your Token

```python
import requests

token = "YOUR_INSTAGRAM_TOKEN"
account_id = "YOUR_ACCOUNT_ID"

# Test 1: Get account info
response = requests.get(
    f"https://graph.instagram.com/v18.0/me?fields=id,username&access_token={token}"
)
print(response.json())

# Test 2: Get posts
response = requests.get(
    f"https://graph.instagram.com/v18.0/{account_id}/media?fields=id,caption&limit=5&access_token={token}"
)
print(response.json())
```

## Common Instagram Errors

### Error: "Invalid OAuth access token"

**Cause:** Token expired or invalid

**Fix:**
1. Get new token from Graph API Explorer
2. Make sure it's an Instagram token (not Facebook token)
3. Token should start with `IG...` or `EAAT...`

### Error: "User does not have permission"

**Cause:** Token doesn't have `instagram_basic` permission

**Fix:**
1. Regenerate token with `instagram_basic` permission
2. Make sure your app has Instagram Basic Display configured

### Error: "Unsupported get request"

**Cause:** Account ID is wrong or account type not supported

**Fix:**
1. Use Business or Creator account (not personal)
2. Verify account ID with `/me` endpoint
3. Make sure account is connected to your app

### Error: "Application does not have permission"

**Cause:** App not configured for Instagram

**Fix:**
1. Go to Facebook Developer Console
2. Add "Instagram Basic Display" or "Instagram Graph API" product
3. Configure Instagram app
4. Regenerate token

## Quick Fix Script

Run this to test and fix:

```bash
cd backend
python fix_instagram_token.py
```

This will:
- ✅ Test your Instagram token
- ✅ Get your account ID automatically
- ✅ Update database with account ID
- ✅ Test media access

## Update .env File

Create `backend/.env` file:

```env
# Instagram
INSTAGRAM_ACCESS_TOKEN=YOUR_INSTAGRAM_TOKEN_HERE
```

## Update Database

After getting account ID, update database:

```python
from database import SessionLocal
from models import Source

db = SessionLocal()
ig = db.query(Source).filter(Source.platform == "Instagram").first()
if ig:
    ig.account_id = "YOUR_ACCOUNT_ID"
    ig.account_handle = "your_username"
    db.commit()
```

Or use the fix script:
```bash
python fix_instagram_token.py
```

## Instagram Token Types

### Short-Lived Token (1 hour)
- From Graph API Explorer
- Expires quickly
- Good for testing

### Long-Lived Token (60 days)
- Exchange short-lived token
- Lasts 60 days
- Better for production

### Page Access Token
- For Instagram Business Accounts
- Connected to Facebook Page
- More stable

## Getting Long-Lived Token

```bash
GET https://graph.instagram.com/oauth/access_token?
  grant_type=ig_exchange_token&
  client_secret=YOUR_APP_SECRET&
  access_token=SHORT_LIVED_TOKEN
```

## Testing After Fix

```bash
# Test token
python fix_instagram_token.py

# Test scraper
python test_facebook_instagram.py

# Trigger scrape
python trigger_scrape.py
```

## Important Notes

1. **Instagram requires Business/Creator account** for API access
2. **Personal accounts** don't work with Instagram Graph API
3. **Token expires** after 60 days (long-lived) or 1 hour (short-lived)
4. **Account must be connected** to your Facebook app
5. **Permissions required**: `instagram_basic` minimum

## Troubleshooting

### "No Instagram access token configured"
- Create `.env` file in `backend/` directory
- Add `INSTAGRAM_ACCESS_TOKEN=your_token`

### "Cannot parse access token"
- Token format is wrong
- Make sure token starts with `IG...` or `EAAT...`
- Get fresh token from Graph API Explorer

### "User does not have permission"
- Token needs `instagram_basic` permission
- Regenerate token with correct permissions
- Make sure app has Instagram product added

### "Account ID not found"
- Use `/me` endpoint to get correct account ID
- Make sure account is Business/Creator type
- Verify account is connected to app

## Next Steps

1. ✅ Get Instagram token from Graph API Explorer
2. ✅ Get account ID using `/me?fields=id,username`
3. ✅ Update `.env` file with token
4. ✅ Run `python fix_instagram_token.py`
5. ✅ Test scraping with `python trigger_scrape.py`

Your Instagram account will be ready once you have a valid token and account ID! 📸
