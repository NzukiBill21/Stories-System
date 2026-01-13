# Facebook & TikTok Quick Start (No Database Needed for Testing)

## Where to Find "Add Product" in Meta Console

**In your screenshot, you're in the right place!**

### Location:

1. **You're here:** "My Apps" tab (top) ✅
2. **Look for:** 
   - **"Add platform"** button (gray button with + icon) - This is it!
   - OR in left sidebar: "Products" section
   - OR in main area: "Products" tab/section

3. **Click "Add platform"** or look for "Products" in the sidebar

**Note:** You don't need to add products for Facebook or TikTok - just tokens! "Add Product" is only needed for Instagram setup (which we're skipping).

## Focus: Facebook & TikTok Only

### Step 1: Test Facebook Directly (No Database)

Create `backend/test_facebook_direct.py`:

```python
import requests
from config import settings

token = settings.facebook_access_token
page_id = "1412325813805867"  # Bee Bill

# Test fetching posts
url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
params = {
    'access_token': token,
    'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
    'limit': 5
}

response = requests.get(url, params=params)
data = response.json()

if 'error' in data:
    print(f"Error: {data['error']['message']}")
else:
    posts = data.get('data', [])
    print(f"Success! Found {len(posts)} posts")
    for post in posts:
        print(f"  - {post.get('message', 'No message')[:50]}...")
        print(f"    Likes: {post.get('likes', {}).get('summary', {}).get('total_count', 0)}")
```

### Step 2: Test TikTok Directly

```python
from TikTokApi import TikTokApi
import asyncio

async def test_tiktok():
    async with TikTokApi() as api:
        trending = api.trending()
        count = 0
        async for video in trending:
            print(f"Video: {video.desc[:50]}...")
            print(f"  Likes: {video.stats.diggCount}")
            count += 1
            if count >= 5:
                break

asyncio.run(test_tiktok())
```

## Fix Database Connection First

Before running the focus script, fix database:

1. **Check `.env` file:**
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_actual_password  # Update this!
   DB_NAME=story_intelligence
   ```

2. **Test connection:**
   ```bash
   python test_db_connection.py
   ```

3. **Then run:**
   ```bash
   python focus_facebook_tiktok.py
   ```

## Quick Test Without Database

Test Facebook scraping directly:

```bash
cd backend
python -c "
import requests
from config import settings

token = settings.facebook_access_token
page_id = '1412325813805867'

url = f'https://graph.facebook.com/v18.0/{page_id}/posts'
params = {'access_token': token, 'fields': 'id,message', 'limit': 3}

r = requests.get(url, params=params)
data = r.json()

if 'error' in data:
    print('Error:', data['error']['message'])
else:
    print(f'Success! Found {len(data.get(\"data\", []))} posts')
"
```

## Summary

**"Add Product" location:**
- Look for "Add platform" button (gray, with + icon)
- Or "Products" section in sidebar
- **But you don't need it for Facebook/TikTok!**

**Next steps:**
1. Fix database password in `.env`
2. Run `python focus_facebook_tiktok.py`
3. Test Facebook: `python test_facebook_instagram.py`
4. Test TikTok: `python test_tiktok_scraper.py`
5. Start scraping!

Focus on Facebook and TikTok - they'll work great! 🚀
