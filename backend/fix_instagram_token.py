"""Quick script to test and fix Instagram token and account ID."""
import requests
from config import settings
from database import SessionLocal
from models import Source
from loguru import logger


def test_instagram_token(token):
    """Test if Instagram token is valid."""
    print(f"Testing Instagram token: {token[:20]}...\n")
    
    # Test 1: Get user info
    print("1. Testing Instagram user info...")
    try:
        response = requests.get(
            f"https://graph.instagram.com/v18.0/me?fields=id,username&access_token={token}",
            timeout=10
        )
        user_data = response.json()
        
        if 'error' in user_data:
            print(f"   [ERROR] {user_data['error']['message']}")
            print(f"   Code: {user_data['error'].get('code')}")
            print(f"   Type: {user_data['error'].get('type')}")
            return False, None, None
        else:
            account_id = user_data.get('id')
            username = user_data.get('username', 'Unknown')
            print(f"   [OK] Token is valid!")
            print(f"   Account ID: {account_id}")
            print(f"   Username: {username}")
            return True, account_id, username
            
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False, None, None


def test_instagram_media(token, account_id):
    """Test fetching Instagram posts."""
    print("\n2. Testing Instagram media access...")
    try:
        response = requests.get(
            f"https://graph.instagram.com/v18.0/{account_id}/media?fields=id,caption,timestamp,permalink,like_count,comments_count&limit=5&access_token={token}",
            timeout=10
        )
        media_data = response.json()
        
        if 'error' in media_data:
            print(f"   [ERROR] {media_data['error']['message']}")
            print(f"   Code: {media_data['error'].get('code')}")
            return False
        else:
            posts = media_data.get('data', [])
            print(f"   [OK] Found {len(posts)} post(s)")
            if posts:
                print(f"   Sample post: {posts[0].get('caption', 'No caption')[:50]}...")
            return True
            
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False


def update_database(account_id, username):
    """Update database with Instagram account info."""
    db = SessionLocal()
    try:
        # Find or create Instagram source
        source = db.query(Source).filter(
            Source.platform == "Instagram"
        ).first()
        
        if source:
            source.account_id = account_id
            source.account_handle = username
            source.account_name = username
            source.is_active = True
            print(f"\n[OK] Updated Instagram source:")
            print(f"     Platform: {source.platform}")
            print(f"     Username: {source.account_handle}")
            print(f"     Account ID: {source.account_id}")
        else:
            source = Source(
                platform="Instagram",
                account_handle=username,
                account_name=username,
                account_id=account_id,
                is_active=True
            )
            db.add(source)
            print(f"\n[OK] Created Instagram source:")
            print(f"     Platform: {source.platform}")
            print(f"     Username: {source.account_handle}")
            print(f"     Account ID: {source.account_id}")
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error updating database: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main function."""
    print("=" * 60)
    print("Instagram Token Tester & Database Updater")
    print("=" * 60)
    print()
    
    token = settings.instagram_access_token
    
    if not token:
        print("[ERROR] No Instagram access token configured in .env")
        print("\nQUICK FIX:")
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Click 'Generate Instagram Access Token' button (blue button on right)")
        print("3. IMPORTANT: Select your Instagram account (NOT 'App Token')")
        print("4. Select permission: instagram_basic")
        print("5. Copy the token (starts with IG... or EAAT...)")
        print("6. Add to .env: INSTAGRAM_ACCESS_TOKEN=your_token")
        print("\nSee: backend/INSTAGRAM_QUICK_FIX.md for detailed guide")
        return 1
    
    # Check if it's an App Token (wrong format)
    if '|' in token and len(token.split('|')) == 2:
        print("[ERROR] You're using an App Token, not a User Access Token!")
        print("\nApp Token format: APP_ID|SECRET (this is WRONG for Instagram)")
        print("User Token format: IG... or EAAT... (this is CORRECT)")
        print("\nTo fix:")
        print("1. In Graph API Explorer, click 'Generate Instagram Access Token'")
        print("2. Select your Instagram account (NOT 'App Token')")
        print("3. Get the user token and update .env")
        print("\nSee: backend/INSTAGRAM_QUICK_FIX.md")
        return 1
    
    # Test token
    is_valid, account_id, username = test_instagram_token(token)
    
    if not is_valid:
        print("\n" + "=" * 60)
        print("TOKEN IS INVALID")
        print("=" * 60)
        print("\nCommon issues:")
        print("1. Token expired (Instagram tokens expire after 60 days)")
        print("2. Token doesn't have 'instagram_basic' permission")
        print("3. Token is for wrong account")
        print("\nTo get a new token:")
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Select your app")
        print("3. Use Instagram access token (not Facebook token)")
        print("4. Query: GET /me?fields=id,username")
        print("5. If error, regenerate token with 'instagram_basic' permission")
        return 1
    
    # Test media access
    if account_id:
        media_ok = test_instagram_media(token, account_id)
        
        if media_ok:
            # Update database
            update_database(account_id, username)
            
            print("\n" + "=" * 60)
            print("NEXT STEPS")
            print("=" * 60)
            print("\n1. Test scraper: python test_facebook_instagram.py")
            print("2. Trigger scrape: python trigger_scrape.py")
            print("\n[OK] Instagram is ready!")
        else:
            print("\n[WARNING] Token works but can't access media")
            print("Token may need 'instagram_basic' or 'instagram_content_publish' permission")
            print("Still updating database with account ID...")
            update_database(account_id, username)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
