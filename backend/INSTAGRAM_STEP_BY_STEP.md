# Instagram Token - Step by Step Fix

## Current Error

```
"Access token does not contain a valid app ID"
Error code: 190
```

## Solution: Get User Access Token (Not App Token)

### Visual Guide

**What you see:**
- Access Token: `1380487200420198|b-plQpbGyXHzI7YioPR1FvYL_5g` ← This is App Token (WRONG)
- "User or Page": App Token ← This is the problem!

**What you need:**
- Access Token: `IG...` or `EAAT...` ← User Token (CORRECT)
- "User or Page": Your Instagram Account ← Select this!

## Step-by-Step Instructions

### Step 1: Generate User Token

1. **In Graph API Explorer, look at the right panel**
2. **Find the blue button:** "Generate Instagram Access Token"
3. **Click it**

### Step 2: Select Your Account

1. **In "User or Page" dropdown:**
   - Currently shows: "App Token" ❌
   - Change to: Your Instagram account name ✅

2. **If you don't see your account:**
   - Your Instagram account needs to be connected to the app
   - Or use a Facebook Page that's connected to Instagram

### Step 3: Select Permissions

1. **Make sure these are checked:**
   - ✅ `instagram_basic`
   - ✅ `instagram_content_publish` (optional)

2. **Click "Generate Access Token"**

### Step 4: Copy the Token

1. **The new token will appear** (starts with `IG...` or `EAAT...`)
2. **Copy it** (click the copy icon)

### Step 5: Test It

1. **In Graph API Explorer:**
   - Make sure "User or Page" shows your account (not "App Token")
   - Query: `GET /me?fields=id,username`
   - Click "Submit"

2. **Should get:**
   ```json
   {
     "id": "17841405309211844",
     "username": "your_username"
   }
   ```

### Step 6: Update .env

Edit `backend/.env`:

```env
INSTAGRAM_ACCESS_TOKEN=IG...your_new_token_here
```

### Step 7: Run Auto-Fix

```bash
cd backend
python fix_instagram_token.py
```

## If You Can't Generate Instagram Token

### Check 1: Instagram Product Added?

1. Go to: https://developers.facebook.com/apps/
2. Select your app ("Stories")
3. Check if "Instagram Basic Display" or "Instagram Graph API" is added
4. If not, click "Add Product" and add it

### Check 2: Account Connected?

1. In your app settings
2. Go to Instagram product
3. Make sure your Instagram account is connected
4. May need to authorize the app

### Check 3: Use Facebook Page Token

If you have a Facebook Page:

1. In Graph API Explorer
2. Select your **Facebook Page** (not App Token)
3. Query: `GET /me/accounts`
4. Get page access token
5. Query: `GET /{page-id}?fields=instagram_business_account`
6. Use the Instagram Business Account ID

## Quick Checklist

- [ ] Clicked "Generate Instagram Access Token" button
- [ ] Selected Instagram account (not "App Token")
- [ ] Selected `instagram_basic` permission
- [ ] Copied the new token (starts with `IG...` or `EAAT...`)
- [ ] Tested with `GET /me?fields=id,username` - works!
- [ ] Updated `.env` file with new token
- [ ] Ran `python fix_instagram_token.py` - success!

## The Key Difference

| Type | Format | Use Case |
|------|--------|----------|
| **App Token** | `APP_ID\|SECRET` | App-level operations ❌ |
| **User Token** | `IG...` or `EAAT...` | User/account operations ✅ |

**Instagram API needs User Token!**

## After Fix

Once you have the correct token:

```bash
# Test
python fix_instagram_token.py

# Should show:
# [OK] Token is valid!
# Account ID: 17841405309211844
# Username: your_username
```

Then you're ready to scrape Instagram! 📸
