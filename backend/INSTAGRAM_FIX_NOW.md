# Instagram Fix - Do This Now!

## The Problem

You're using an **App Token** (`1380487200420198|b-plQpbGyXHzI7YioPR1FvYL_5g`) but Instagram needs a **User Access Token**.

## Fix in 3 Steps

### Step 1: Generate User Token (30 seconds)

In Graph API Explorer:

1. **Look at the RIGHT side panel**
2. **Find the BLUE button:** "Generate Instagram Access Token"
3. **Click it!**

### Step 2: Select Your Account (10 seconds)

1. **In the dropdown "User or Page":**
   - Currently: "App Token" ❌
   - Change to: **Your Instagram account** ✅
   - (If you don't see it, select a Facebook Page connected to Instagram)

2. **Select permission:**
   - ✅ `instagram_basic`

3. **Click "Generate Access Token"**

### Step 3: Copy & Update (30 seconds)

1. **Copy the new token** (starts with `IG...` or `EAAT...`)

2. **Edit `backend/.env` file:**
   ```env
   INSTAGRAM_ACCESS_TOKEN=IG...paste_your_new_token_here
   ```

3. **Test:**
   ```bash
   python fix_instagram_token.py
   ```

## Visual Guide

**WRONG (What you have now):**
```
Access Token: 1380487200420198|b-plQpbGyXHzI7YioPR1FvYL_5g
User or Page: App Token
```

**CORRECT (What you need):**
```
Access Token: IGQWRNy... (or EAATni...)
User or Page: Your Instagram Account Name
```

## If "Generate Instagram Access Token" Button Doesn't Work

### Option A: Add Instagram Product

1. Go to: https://developers.facebook.com/apps/
2. Select your app ("Stories")
3. Click "Add Product"
4. Add "Instagram Basic Display"
5. Configure it
6. Go back to Graph API Explorer
7. Try again

### Option B: Use Facebook Page Token

1. In Graph API Explorer
2. Select your **Facebook Page** (not App Token)
3. Query: `GET /me/accounts`
4. Get the page access token
5. Query: `GET /{page-id}?fields=instagram_business_account`
6. Use that Instagram account ID

## Quick Test

After updating `.env`:

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

## The Key

**App Token** = For app operations (doesn't work with Instagram API)  
**User Token** = For user/account operations (this is what you need!)

Click that blue button and select your account! 🔵
