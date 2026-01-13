# Update Expired Facebook Token

## Issue
Your Facebook access token expired on Friday, 09-Jan-26.

## Quick Fix

### Step 1: Get New Token

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app from the dropdown
3. Click "Generate Access Token"
4. Select permissions:
   - `pages_read_engagement`
   - `pages_show_list`
   - `pages_read_user_content`
5. Copy the token (starts with `EAAT...`)

### Step 2: Update .env File

Open `backend/.env` and update:
```
FACEBOOK_ACCESS_TOKEN=YOUR_NEW_TOKEN_HERE
```

### Step 3: Test Token

```bash
python test_new_facebook_token.py
```

### Step 4: Run Scraping Again

```bash
python scrape_facebook_trends.py
```

## Note

Facebook tokens typically expire after 60 days. For production, consider:
- Using a long-lived token
- Setting up token refresh automation
- Using a Facebook App with extended permissions
