"""Verify database connection and help fix issues."""
import pymysql
from config import settings
import sys

def test_connection_with_details():
    """Test connection and show detailed error info."""
    print("=" * 60)
    print("Database Connection Verification")
    print("=" * 60)
    print()
    
    print("Current settings:")
    print(f"  Host: {settings.db_host}")
    print(f"  Port: {settings.db_port}")
    print(f"  User: {settings.db_user}")
    print(f"  Database: {settings.db_name}")
    print(f"  Password: {'*' * len(settings.db_password) if settings.db_password else '(empty)'}")
    print(f"  Password length: {len(settings.db_password) if settings.db_password else 0}")
    
    # Check for common issues
    if settings.db_password:
        if settings.db_password.startswith('"') or settings.db_password.startswith("'"):
            print("\n[WARNING] Password appears to have quotes - remove them!")
        if settings.db_password.endswith('"') or settings.db_password.endswith("'"):
            print("[WARNING] Password appears to have quotes - remove them!")
        if settings.db_password.strip() != settings.db_password:
            print("[WARNING] Password has leading/trailing whitespace - remove it!")
    
    print("\nTesting connection...")
    
    try:
        # Try connecting
        connection = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            connect_timeout=5
        )
        
        print("[OK] Connection successful!")
        
        # Test query
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"[OK] MySQL version: {version[0]}")
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"[OK] Found {len(tables)} table(s)")
        
        if tables:
            print("Tables:", ", ".join([t[0] for t in tables]))
        else:
            print("[INFO] No tables found - run 'python init_db.py' to create them")
        
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        error_msg = e.args[1]
        
        print(f"\n[ERROR] Connection failed!")
        print(f"Error code: {error_code}")
        print(f"Error message: {error_msg}")
        
        if error_code == 1045:
            print("\n" + "=" * 60)
            print("ACCESS DENIED - Password Issue")
            print("=" * 60)
            print("\nPossible causes:")
            print("1. Wrong password in .env file")
            print("2. Password has quotes or spaces (remove them)")
            print("3. Username is wrong")
            print("\nTo fix:")
            print("1. Open backend/.env")
            print("2. Find: DB_PASSWORD=...")
            print("3. Make sure password has NO quotes, NO spaces")
            print("4. Example: DB_PASSWORD=mypassword123")
            print("5. NOT: DB_PASSWORD='mypassword123'")
            print("6. NOT: DB_PASSWORD= mypassword123")
            
        elif error_code == 1049:
            print(f"\nDatabase '{settings.db_name}' does not exist")
            print("Run: python init_db.py")
            
        elif error_code == 2003:
            print("\nCannot connect to MySQL server")
            print("Check if MySQL is running")
            
        return False
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

def main():
    """Main function."""
    success = test_connection_with_details()
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS! Database is ready")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python focus_facebook_tiktok.py")
        print("2. Run: python trigger_scrape.py")
        return 0
    else:
        print("\n" + "=" * 60)
        print("FIX NEEDED")
        print("=" * 60)
        print("\nAfter fixing, run this script again:")
        print("  python verify_and_fix_db.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
