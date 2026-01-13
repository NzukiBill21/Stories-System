"""Test the new Facebook token you provided."""
import requests

# Your new token
NEW_TOKEN = "EAATni7kysWYBQQiE6VY53hSN3Kh9deIhqYlHfMsJxRHRG3cvgW2oCEjuCZAZC3GNSfdy5S2ZCC6qaKnA7fmCZBYIZBG5KyYyDhrmhuZB5QaWEjkFCcz7omUAPPZB3xZCp5zl1EUgZCAdRCrprQzmhIYLSzOl6C3IFcOZAlZBWGWEdtslB3ZBVoy5OpZAlUpfDmoDGgrabHw9JZCLRadxC92aO5CnMuRZBMD4SZBeHPmczlv8cmbrU4Rx5ZAK8gj7KnIKpZAL4ZB9Q2Q4Dc3EDMZCttt9AHJ2ARs2"

PAGE_ID = "1412325813805867"  # Bee Bill

def main():
    """Test new Facebook token."""
    print("=" * 60)
    print("Testing New Facebook Token")
    print("=" * 60)
    print()
    
    print(f"Page ID: {PAGE_ID} (Bee Bill)")
    print(f"Token: {NEW_TOKEN[:30]}...\n")
    
    # Test 1: Get page info
    print("1. Getting page info...")
    try:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}"
        params = {'access_token': NEW_TOKEN, 'fields': 'id,name'}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            print(f"   [ERROR] {data['error']['message']}")
            print(f"   Code: {data['error'].get('code')}")
            return 1
        
        print(f"   [OK] Page: {data.get('name')} (ID: {data.get('id')})")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return 1
    
    # Test 2: Get posts
    print("\n2. Fetching posts...")
    try:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/posts"
        params = {
            'access_token': NEW_TOKEN,
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
                created = post.get('created_time', '')[:10]
                print(f"\n   {i}. {message}...")
                print(f"      Date: {created}")
                print(f"      Likes: {likes}, Comments: {comments}, Shares: {shares}")
        
        print("\n" + "=" * 60)
        print("[OK] NEW TOKEN WORKS!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update backend/.env file:")
        print("   Change FACEBOOK_ACCESS_TOKEN to:")
        print(f"   FACEBOOK_ACCESS_TOKEN={NEW_TOKEN}")
        print("\n2. Then run:")
        print("   python focus_facebook_tiktok.py")
        print("   python trigger_scrape.py")
        
        return 0
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
