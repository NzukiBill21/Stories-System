"""Quick script to test and update Facebook token."""
import requests
from config import settings
from database import SessionLocal
from models import Source

def test_token(token):
    """Test if Facebook token is valid."""
    print(f"Testing token: {token[:20]}...\n")
    
    # Test 1: Get user info
    print("1. Testing user info...")
    response = requests.get(
        f"https://graph.facebook.com/v18.0/me?access_token={token}",
        timeout=10
    )
    user_data = response.json()
    
    if 'error' in user_data:
        print(f"   [ERROR] {user_data['error']['message']}")
        return False, None
    else:
        print(f"   [OK] Token is valid!")
        print(f"   User: {user_data.get('name', 'Unknown')} (ID: {user_data.get('id')})")
    
    # Test 2: Get pages
    print("\n2. Testing pages access...")
    response = requests.get(
        f"https://graph.facebook.com/v18.0/me/accounts?access_token={token}",
        timeout=10
    )
    pages_data = response.json()
    
    if 'error' in pages_data:
        print(f"   [ERROR] {pages_data['error']['message']}")
        print(f"   Token may not have 'pages_read_engagement' permission")
        return True, None
    else:
        pages = pages_data.get('data', [])
        print(f"   [OK] Found {len(pages)} page(s) you manage:")
        
        page_tokens = {}
        for page in pages:
            page_id = page.get('id')
            page_name = page.get('name')
            page_token = page.get('access_token')
            print(f"   - {page_name} (ID: {page_id})")
            print(f"     Page Token: {page_token[:30]}...")
            page_tokens[page_id] = {
                'name': page_name,
                'token': page_token
            }
        
        return True, page_tokens


def update_database(page_id, page_name, page_token=None):
    """Update database with page information."""
    db = SessionLocal()
    try:
        # Find or create Facebook source
        source = db.query(Source).filter(
            Source.platform == "Facebook",
            Source.account_id == page_id
        ).first()
        
        if not source:
            # Check if any Facebook source exists
            source = db.query(Source).filter(Source.platform == "Facebook").first()
        
        if source:
            source.account_id = page_id
            source.account_handle = page_name
            source.account_name = page_name
            source.is_active = True
            print(f"\n[OK] Updated source: {page_name} (ID: {page_id})")
        else:
            source = Source(
                platform="Facebook",
                account_handle=page_name,
                account_name=page_name,
                account_id=page_id,
                is_active=True
            )
            db.add(source)
            print(f"\n[OK] Created source: {page_name} (ID: {page_id})")
        
        db.commit()
        
        # Note about token
        if page_token:
            print(f"\n[IMPORTANT] Update your .env file with the PAGE token:")
            print(f"   FACEBOOK_ACCESS_TOKEN={page_token}")
            print(f"   (Page tokens are better than user tokens for scraping)")
        
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
    print("Facebook Token Tester & Database Updater")
    print("=" * 60)
    print()
    
    token = settings.facebook_access_token
    
    if not token:
        print("[ERROR] No Facebook access token configured in .env")
        print("\nTo fix:")
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Generate access token with 'pages_read_engagement' permission")
        print("3. Add to .env: FACEBOOK_ACCESS_TOKEN=your_token")
        return 1
    
    # Test token
    is_valid, page_tokens = test_token(token)
    
    if not is_valid:
        print("\n" + "=" * 60)
        print("TOKEN IS INVALID")
        print("=" * 60)
        print("\nTo get a new token:")
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Select your app")
        print("3. Click 'Generate Access Token'")
        print("4. Select permissions: pages_read_engagement, pages_show_list")
        print("5. Copy the token and update .env file")
        return 1
    
    # If we have page tokens, offer to update database
    if page_tokens:
        print("\n" + "=" * 60)
        print("UPDATE DATABASE")
        print("=" * 60)
        
        if len(page_tokens) == 1:
            # Only one page, update automatically
            page_id = list(page_tokens.keys())[0]
            page_info = page_tokens[page_id]
            update_database(page_id, page_info['name'], page_info['token'])
        else:
            # Multiple pages, let user choose
            print("\nMultiple pages found. Which one to use?")
            pages_list = list(page_tokens.items())
            for i, (page_id, page_info) in enumerate(pages_list, 1):
                print(f"{i}. {page_info['name']} (ID: {page_id})")
            
            try:
                choice = input("\nEnter number (or 'all' for all): ").strip()
                if choice.lower() == 'all':
                    for page_id, page_info in pages_list:
                        update_database(page_id, page_info['name'], page_info['token'])
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(pages_list):
                        page_id, page_info = pages_list[idx]
                        update_database(page_id, page_info['name'], page_info['token'])
                    else:
                        print("Invalid choice")
            except (ValueError, KeyboardInterrupt):
                print("\nCancelled")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. If you got a PAGE token, update .env with it")
    print("2. Test scraper: python test_facebook_instagram.py")
    print("3. Trigger scrape: python trigger_scrape.py")
    print("\n[OK] Done!")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
