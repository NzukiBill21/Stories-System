"""Helper script to create .env file from env.example."""
import os
import shutil

def main():
    """Create .env file if it doesn't exist."""
    env_example = "env.example"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"[OK] .env file already exists")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Cancelled")
            return 0
    
    if not os.path.exists(env_example):
        print(f"[ERROR] {env_example} not found")
        return 1
    
    # Copy env.example to .env
    shutil.copy(env_example, env_file)
    print(f"[OK] Created .env file from {env_example}")
    print(f"\nNext steps:")
    print(f"1. Edit {env_file} and add your tokens:")
    print(f"   - FACEBOOK_ACCESS_TOKEN=your_facebook_token")
    print(f"   - INSTAGRAM_ACCESS_TOKEN=your_instagram_token")
    print(f"2. Update database credentials if needed")
    print(f"3. Run: python fix_instagram_token.py")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
