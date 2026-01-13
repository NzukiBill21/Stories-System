# Instagram Token Quick Fix - "Access token does not contain a valid app ID"

## The Problem

You're seeing:
```
"Access token does not contain a valid app ID"
Error code: 190
```

**Cause:** You're using an **App Token** instead of a **User Access Token**

## Quick Fix (2 minutes)

### Step 1: Generate User Access Token

In Graph API Explorer:

1. **Click the blue button:** "Generate Instagram Access Token"
   - (It's on the right side, below the Access Token field)

2. **Select User/Page:**
   - In the "User or Page" dropdown
   - Change from "App Token" to your **Instagram account** or **Page**
   - If you don't see your account, you may need to:
     - Add Instagram product to your app
     - Connect your Instagram account to the app

3. **Select Permissions:**
   - Make sure `instagram_basic` is selected
   - Click "Generate Access Token"

4. **Copy the New Token:**
   - The token will start with `IG...` or `EAAT...`
   - This is your **User Access Token** (not App Token)

### Step 2: Test the Token

In Graph API Explorer:

1. **Make sure "User or Page" is NOT "App Token"**
2. **Query:** `GET /me?fields=id,username`
3. **Click "Submit"**

You should get:
```json
{
  "id": "17841405309211844",
  "username": "your_username"
}
```

### Step 3: Update .env File

Edit `backend/.env`:

```env
INSTAGRAM_ACCESS_TOKEN=your_new_user_token_here
```

(Replace `your_new_user_token_here` with the token you just generated)

### Step 4: Run Fix Script

```bash
cd backend
python fix_instagram_token.py
```

This will:
- ✅ Test your token
- ✅ Get your account ID
- ✅ Update database automatically

## Why This Happened

- **App Token** (`1380487200420198|b-plQpbGyXHzI7YioPR1FvYL_5g`) = For app-level operations
- **User Access Token** (`IG...` or `EAAT...`) = For user/account operations

Instagram API needs **User Access Token**, not App Token!

## If "Generate Instagram Access Token" Doesn't Work

### Option 1: Add Instagram Product to App

1. Go to: https://developers.facebook.com/apps/
2. Select your app
3. Click "Add Product"
4. Add "Instagram Basic Display" or "Instagram Graph API"
5. Configure it
6. Go back to Graph API Explorer
7. Try generating token again

### Option 2: Use Facebook Page Token

If you have a Facebook Page connected to Instagram:

1. In Graph API Explorer
2. Select your **Facebook Page** (not App Token)
3. Query: `GET /me/accounts`
4. Find your page
5. Use the page's access token
6. Query Instagram: `GET /{page-id}?fields=instagram_business_account`

## Quick Test

After getting the token:

```bash
cd backend
python fix_instagram_token.py
```

Should show:
```
[OK] Token is valid!
Account ID: 17841405309211844
Username: your_username
```

## Summary

**The Fix:**
1. Click "Generate Instagram Access Token" button
2. Select your Instagram account (NOT "App Token")
3. Copy the new token
4. Update `.env` file
5. Run `python fix_instagram_token.py`

**The Issue:** App Token ≠ User Token. Instagram needs User Token! 🔑
