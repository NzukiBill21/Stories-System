"""Test Facebook scraping directly without database."""
import requests
from config import settings

def main():
    """Test Facebook API directly."""
    print("=" * 60)
    print("Facebook Direct Test (No Database)")
    print("=" * 60)
    print()
    
    token = settings.facebook_access_token
    if not token:
        print("[ERROR] Facebook token not in .env")
        print("Add: FACEBOOK_ACCESS_TOKEN=your_token")
        return 1
    
    page_id = "1412325813805867"  # Bee Bill
    
    print(f"Testing Facebook page: {page_id} (Bee Bill)")
    print(f"Token: {token[:30]}...\n")
    
    # Test 1: Get page info
    print("1. Getting page info...")
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {'access_token': token, 'fields': 'id,name'}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            print(f"   [ERROR] {data['error']['message']}")
            return 1
        
        print(f"   [OK] Page: {data.get('name')} (ID: {data.get('id')})")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return 1
    
    # Test 2: Get posts
    print("\n2. Fetching posts...")
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
        params = {
            'access_token': token,
            'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
            'limit': 5
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            error = data['error']
            print(f"   [ERROR] {error.get('message')}")
            print(f"   Code: {error.get('code')}")
            if error.get('code') == 190:
                print(f"   Token is invalid or expired")
            elif error.get('code') == 200:
                print(f"   Permission denied - token needs 'pages_read_engagement'")
            return 1
        
        posts = data.get('data', [])
        print(f"   [OK] Found {len(posts)} post(s)!\n")
        
        if posts:
            print("Sample posts:")
            for i, post in enumerate(posts, 1):
                message = post.get('message', 'No message')[:60]
                likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                shares = post.get('shares', {}).get('count', 0)
                print(f"\n   {i}. {message}...")
                print(f"      Likes: {likes}, Comments: {comments}, Shares: {shares}")
        
        print("\n" + "=" * 60)
        print("[OK] Facebook is working!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Fix database connection (update DB_PASSWORD in .env)")
        print("2. Run: python focus_facebook_tiktok.py")
        print("3. Run: python trigger_scrape.py")
        print("4. Check dashboard for Facebook stories!")
        
        return 0
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
