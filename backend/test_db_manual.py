"""Manual database connection test with user input."""
import pymysql
from getpass import getpass

def main():
    """Test database connection manually."""
    print("=" * 60)
    print("Manual Database Connection Test")
    print("=" * 60)
    print()
    
    print("Enter MySQL credentials:")
    host = input("Host [localhost]: ").strip() or "localhost"
    port = int(input("Port [3306]: ").strip() or "3306")
    user = input("User [root]: ").strip() or "root"
    password = getpass("Password: ")
    database = input("Database [story_intelligence]: ").strip() or "story_intelligence"
    
    print("\nTesting connection...")
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5
        )
        print("[OK] Connection successful!")
        
        # Test query
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"[OK] MySQL version: {version[0]}")
        
        # Check if database exists and has tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"[OK] Found {len(tables)} table(s) in database")
        
        connection.close()
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print("\nIf this worked, update your .env file with:")
        print(f"DB_HOST={host}")
        print(f"DB_PORT={port}")
        print(f"DB_USER={user}")
        print(f"DB_PASSWORD={password}")
        print(f"DB_NAME={database}")
        
        return 0
        
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        error_msg = e.args[1]
        print(f"[ERROR] {error_msg}")
        print(f"Error code: {error_code}")
        
        if error_code == 1045:
            print("\nAccess denied - Wrong password or username")
        elif error_code == 1049:
            print(f"\nDatabase '{database}' does not exist")
            print("Run: python init_db.py")
        elif error_code == 2003:
            print("\nCannot connect to MySQL server")
            print("Check if MySQL is running")
        
        return 1
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
