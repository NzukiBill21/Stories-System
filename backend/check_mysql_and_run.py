"""
Check if MySQL is running, then run Facebook trends scraping.
"""
import sys
from database import test_connection

def main():
    print("=" * 60)
    print("MySQL Connection Check & Facebook Trends Scraper")
    print("=" * 60)
    print()
    
    # Check MySQL connection
    print("Checking MySQL connection...")
    if not test_connection():
        print()
        print("[ERROR] MySQL is not running!")
        print()
        print("Please start MySQL:")
        print("  1. Open XAMPP/WAMP Control Panel")
        print("  2. Click 'Start' for MySQL")
        print("  OR")
        print("  3. Open Services (Win+R, type 'services.msc')")
        print("  4. Find 'MySQL' service and start it")
        print()
        print("Then run this script again.")
        return 1
    
    print("[OK] MySQL is running!")
    print()
    
    # Import and run scraping
    print("Running Facebook trends scraping...")
    print()
    
    try:
        from scrape_facebook_trends import main as scrape_main
        return scrape_main()
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
