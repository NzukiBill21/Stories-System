# Instagram & Facebook Status

## ✅ Facebook - READY!

**Status:** Configured and ready
- **Page ID**: `1412325813805867`
- **Page Name**: "Bee Bill"
- **Database**: Updated ✅
- **Token**: Needs to be updated in `.env` (expired)

**Next Step:** Get new Facebook token and add to `.env`

## ⚠️ Instagram - NEEDS TOKEN FIX

**Status:** Token error - needs new token and account ID

**Error:** "Invalid OAuth access token - Cannot parse access token"

## Quick Fix for Instagram

### Step 1: Get Instagram Token & Account ID

1. **Go to Graph API Explorer:**
   https://developers.facebook.com/tools/explorer/

2. **Use Instagram Token:**
   - Make sure you're using Instagram access token (not Facebook)
   - Token should have `instagram_basic` permission

3. **Get Account ID:**
   - Query: `GET /me?fields=id,username`
   - Response will be:
     ```json
     {
       "id": "17841405309211844",
       "username": "your_username"
     }
     ```
   - **Copy the `id`** - this is your Instagram Account ID

### Step 2: Update .env File

Edit `backend/.env`:

```env
FACEBOOK_ACCESS_TOKEN=your_facebook_token_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_token_here
```

### Step 3: Run Fix Script

```bash
cd backend
python fix_instagram_token.py
```

This will:
- ✅ Test your Instagram token
- ✅ Get your account ID automatically
- ✅ Update database with account ID
- ✅ Test media access

## Current Setup

### Facebook
- ✅ Page ID: `1412325813805867` (Bee Bill)
- ✅ Database updated
- ⚠️ Need: Valid token in `.env`

### Instagram
- ⚠️ Need: Valid token in `.env`
- ⚠️ Need: Account ID (will be auto-detected by script)

## Test Everything

After updating tokens:

```bash
# Test Instagram
python fix_instagram_token.py

# Test both
python test_facebook_instagram.py

# Trigger scraping
python trigger_scrape.py
```

## Common Instagram Issues

### "Invalid OAuth access token"
- Token expired (Instagram tokens expire after 60 days)
- Get new token from Graph API Explorer
- Make sure it's Instagram token (not Facebook)

### "User does not have permission"
- Token needs `instagram_basic` permission
- Regenerate token with correct permissions

### "Unsupported get request"
- Account must be Business or Creator type
- Personal accounts don't work with Instagram API
- Verify account is connected to your app

## Summary

**Facebook:** ✅ Ready (just need new token)
**Instagram:** ⚠️ Need token + account ID

**Quick Steps:**
1. Get Instagram token from Graph API Explorer
2. Query `GET /me?fields=id,username` to get account ID
3. Update `.env` with Instagram token
4. Run `python fix_instagram_token.py` (auto-updates database)
5. Get new Facebook token and update `.env`
6. Test with `python test_facebook_instagram.py`

See `backend/INSTAGRAM_TOKEN_FIX.md` for detailed guide! 📸
