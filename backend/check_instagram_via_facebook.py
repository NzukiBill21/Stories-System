"""Check if Facebook page has Instagram Business Account and get Instagram ID."""
import requests
from config import settings
from database import SessionLocal
from models import Source

def main():
    """Check Instagram via Facebook page."""
    print("=" * 60)
    print("Instagram via Facebook Page Check")
    print("=" * 60)
    print()
    
    fb_token = settings.facebook_access_token
    if not fb_token:
        print("[ERROR] Facebook token not configured")
        return 1
    
    # Your Facebook page ID
    page_id = "1412325813805867"  # Bee Bill
    
    print(f"Checking Facebook page: {page_id} (Bee Bill)")
    print(f"Token: {fb_token[:30]}...\n")
    
    # Check if page has Instagram Business Account
    print("1. Checking for Instagram Business Account...")
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'fields': 'instagram_business_account',
            'access_token': fb_token
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            print(f"   [ERROR] {data['error']['message']}")
            return 1
        
        ig_account = data.get('instagram_business_account')
        
        if ig_account:
            ig_id = ig_account.get('id')
            ig_username = ig_account.get('username', 'Unknown')
            print(f"   [OK] Found Instagram Business Account!")
            print(f"   Instagram ID: {ig_id}")
            print(f"   Username: {ig_username}")
            
            # Test fetching Instagram posts
            print("\n2. Testing Instagram posts access...")
            ig_url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
            params = {
                'fields': 'id,caption,timestamp,permalink,like_count,comments_count',
                'limit': 5,
                'access_token': fb_token
            }
            
            response = requests.get(ig_url, params=params, timeout=10)
            ig_data = response.json()
            
            if 'error' in ig_data:
                print(f"   [ERROR] {ig_data['error']['message']}")
                print(f"   Code: {ig_data['error'].get('code')}")
            else:
                posts = ig_data.get('data', [])
                print(f"   [OK] Found {len(posts)} Instagram post(s)!")
                if posts:
                    print(f"   Sample: {posts[0].get('caption', 'No caption')[:50]}...")
            
            # Update database
            print("\n3. Updating database...")
            db = SessionLocal()
            try:
                source = db.query(Source).filter(Source.platform == "Instagram").first()
                if source:
                    source.account_id = ig_id
                    source.account_handle = ig_username
                    source.account_name = ig_username
                    source.is_active = True
                    print(f"   [OK] Updated Instagram source:")
                    print(f"        ID: {ig_id}")
                    print(f"        Username: {ig_username}")
                else:
                    source = Source(
                        platform="Instagram",
                        account_handle=ig_username,
                        account_name=ig_username,
                        account_id=ig_id,
                        is_active=True
                    )
                    db.add(source)
                    print(f"   [OK] Created Instagram source")
                
                db.commit()
                print("\n[OK] Instagram configured via Facebook page!")
                print("\nNote: Instagram scraper will use Facebook token automatically")
                print("      (Updated scraper to handle this)")
                
            except Exception as e:
                print(f"   [ERROR] {e}")
                db.rollback()
            finally:
                db.close()
            
            return 0
        else:
            print(f"   [WARNING] Page does not have Instagram Business Account connected")
            print(f"\nTo connect Instagram:")
            print(f"1. Go to Facebook Page Settings")
            print(f"2. Connect Instagram account")
            print(f"3. Or use Instagram Basic Display API (requires app setup)")
            return 1
            
    except Exception as e:
        print(f"   [ERROR] {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
