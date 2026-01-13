"""Script to help update Facebook token in .env file."""
import os
import re

def update_env_token():
    """Update Facebook token in .env file."""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print(f"[ERROR] {env_path} file not found")
        return False
    
    # New token
    new_token = "EAATni7kysWYBQQiE6VY53hSN3Kh9deIhqYlHfMsJxRHRG3cvgW2oCEjuCZAZC3GNSfdy5S2ZCC6qaKnA7fmCZBYIZBG5KyYyDhrmhuZB5QaWEjkFCcz7omUAPPZB3xZCp5zl1EUgZCAdRCrprQzmhIYLSzOl6C3IFcOZAlZBWGWEdtslB3ZBVoy5OpZAlUpfDmoDGgrabHw9JZCLRadxC92aO5CnMuRZBMD4SZBeHPmczlv8cmbrU4Rx5ZAK8gj7KnIKpZAL4ZB9Q2Q4Dc3EDMZCttt9AHJ2ARs2"
    
    # Read current file
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if token exists
    if 'FACEBOOK_ACCESS_TOKEN=' not in content:
        print("[ERROR] FACEBOOK_ACCESS_TOKEN not found in .env")
        return False
    
    # Replace token (handle different formats)
    old_pattern = r'FACEBOOK_ACCESS_TOKEN=.*'
    new_line = f'FACEBOOK_ACCESS_TOKEN={new_token}'
    
    # Check if already updated
    if new_token in content:
        print("[OK] Token already updated in .env")
        return True
    
    # Replace
    new_content = re.sub(old_pattern, new_line, content, flags=re.MULTILINE)
    
    # Write back
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[OK] Token updated in .env file")
    print(f"New token: {new_token[:30]}...")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Update Facebook Token in .env")
    print("=" * 60)
    print()
    
    if update_env_token():
        print("\n[OK] Done! Now test with:")
        print("   python test_facebook_direct.py")
    else:
        print("\n[ERROR] Could not update token")
        print("Please update .env manually")
