"""Check what tokens and permissions are available."""
import requests
from config import settings
from loguru import logger

def test_endpoint(name, url):
    """Test an API endpoint."""
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'error' in data:
            error = data['error']
            return False, f"{error.get('message')} (Code: {error.get('code')})", None
        else:
            return True, "Success", data
    except Exception as e:
        return False, str(e), None


def main():
    """Check available tokens and permissions."""
    print("=" * 60)
    print("Token & Permission Checker")
    print("=" * 60)
    print()
    
    # Check Facebook token
    fb_token = settings.facebook_access_token
    if fb_token:
        print("FACEBOOK TOKEN:")
        print(f"  Token: {fb_token[:30]}...")
        
        # Test Facebook user
        success, msg, data = test_endpoint(
            "Facebook User",
            f"https://graph.facebook.com/v18.0/me?access_token={fb_token}"
        )
        if success:
            print(f"  [OK] User: {data.get('name', 'Unknown')} (ID: {data.get('id')})")
        else:
            print(f"  [ERROR] User: {msg}")
        
        # Test Facebook pages
        success, msg, data = test_endpoint(
            "Facebook Pages",
            f"https://graph.facebook.com/v18.0/me/accounts?access_token={fb_token}"
        )
        if success:
            pages = data.get('data', [])
            print(f"  [OK] Pages: {len(pages)} page(s) found")
            for page in pages[:3]:
                page_id = page.get('id')
                page_name = page.get('name')
                page_token = page.get('access_token', '')[:30]
                print(f"     - {page_name} (ID: {page_id})")
                print(f"       Token: {page_token}...")
                
                # Check if page has Instagram
                ig_check = test_endpoint(
                    "Instagram Check",
                    f"https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account&access_token={fb_token}"
                )
                if ig_check[0] and ig_check[2] and ig_check[2].get('instagram_business_account'):
                    ig_id = ig_check[2]['instagram_business_account']['id']
                    print(f"       [OK] Has Instagram: {ig_id}")
                    print(f"       💡 Use page token for Instagram scraping!")
        else:
            print(f"  [ERROR] Pages: {msg}")
        
        print()
    
    # Check Instagram token
    ig_token = settings.instagram_access_token
    if ig_token:
        print("INSTAGRAM TOKEN:")
        print(f"  Token: {ig_token[:30]}...")
        
        # Check if it's an App Token
        if '|' in ig_token and len(ig_token.split('|')) == 2:
            print(f"  ⚠️  This is an App Token (won't work with Instagram API)")
            print(f"     Format: APP_ID|SECRET")
            print(f"     Need: User Access Token (starts with IG... or EAAT...)")
        else:
            # Test Instagram user
            success, msg, data = test_endpoint(
                "Instagram User",
                f"https://graph.instagram.com/v18.0/me?fields=id,username&access_token={ig_token}"
            )
            if success:
                print(f"  [OK] Account: {data.get('username', 'Unknown')} (ID: {data.get('id')})")
            else:
                print(f"  [ERROR] Account: {msg}")
                print(f"     This might be a Facebook token, not Instagram token")
        
        print()
    
    # Recommendations
    print("=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print()
    
    if fb_token:
        print("[OK] Facebook token is configured")
        print("   - Use Facebook page token for Instagram if page is connected")
        print("   - Query: GET /{page-id}?fields=instagram_business_account")
    
    if ig_token:
        if '|' in ig_token:
            print("[ERROR] Instagram token is App Token (invalid)")
            print("   - Need to generate User Access Token")
            print("   - Add Instagram product to your app first")
        else:
            print("[WARNING] Instagram token may be invalid or wrong type")
            print("   - Try using Facebook page token instead")
            print("   - Or add Instagram product to app")
    
    print("\nNext steps:")
    print("1. If Facebook page has Instagram: Use page token")
    print("2. If not: Add Instagram product to app")
    print("3. Or: Skip Instagram for now, use other platforms")


if __name__ == "__main__":
    main()
