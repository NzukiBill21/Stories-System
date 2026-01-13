"""Help fix database connection issues."""
import pymysql
from config import settings

def test_connection(host, port, user, password, database):
    """Test MySQL connection with given credentials."""
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5
        )
        connection.close()
        return True, "Connection successful!"
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        error_msg = e.args[1]
        
        if error_code == 1045:
            return False, "Access denied - Wrong password or username"
        elif error_code == 1049:
            return False, f"Database '{database}' does not exist"
        elif error_code == 2003:
            return False, "Cannot connect to MySQL server - Check if MySQL is running"
        else:
            return False, f"Error {error_code}: {error_msg}"
    except Exception as e:
        return False, str(e)

def main():
    """Help user fix database connection."""
    print("=" * 60)
    print("Database Connection Fixer")
    print("=" * 60)
    print()
    
    print("Current settings from .env:")
    print(f"  Host: {settings.db_host}")
    print(f"  Port: {settings.db_port}")
    print(f"  User: {settings.db_user}")
    print(f"  Database: {settings.db_name}")
    print(f"  Password: {'*' * len(settings.db_password) if settings.db_password else '(empty)'}")
    print()
    
    # Test current connection
    print("Testing current connection...")
    success, message = test_connection(
        settings.db_host,
        settings.db_port,
        settings.db_user,
        settings.db_password,
        settings.db_name
    )
    
    if success:
        print(f"[OK] {message}")
        print("\nDatabase connection is working!")
        return 0
    else:
        print(f"[ERROR] {message}")
        print()
        print("=" * 60)
        print("HOW TO FIX")
        print("=" * 60)
        print()
        print("1. Check your MySQL password:")
        print("   - Open MySQL command line or MySQL Workbench")
        print("   - Try logging in with: mysql -u root -p")
        print()
        print("2. Update backend/.env file:")
        print("   DB_PASSWORD=your_actual_mysql_password")
        print()
        print("3. Common issues:")
        print("   - Wrong password: Update DB_PASSWORD in .env")
        print("   - MySQL not running: Start MySQL service")
        print("   - Database doesn't exist: Run 'python init_db.py'")
        print()
        print("4. If you don't know your MySQL password:")
        print("   - Reset it in MySQL")
        print("   - Or create a new user:")
        print("     CREATE USER 'story_user'@'localhost' IDENTIFIED BY 'your_password';")
        print("     GRANT ALL PRIVILEGES ON story_intelligence.* TO 'story_user'@'localhost';")
        print()
        print("5. After fixing, test again:")
        print("   python fix_database_connection.py")
        
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
