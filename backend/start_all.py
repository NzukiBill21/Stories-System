"""Helper script to start all backend services."""
import subprocess
import sys
import time
import os
from database import test_connection
from loguru import logger


def check_requirements():
    """Check if all requirements are met."""
    print("Checking requirements...")
    
    # Check database
    if not test_connection():
        print("✗ Database connection failed!")
        print("  Run: python test_db_connection.py")
        return False
    print("✓ Database connected")
    
    # Check Redis (optional, but needed for Celery)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis connected")
    except:
        print("⚠ Redis not available (Celery won't work)")
        print("  Install Redis or start Redis server")
    
    return True


def start_api():
    """Start the FastAPI server."""
    print("\nStarting API server...")
    print("  API will be at: http://localhost:8000")
    print("  API docs at: http://localhost:8000/docs")
    print("  Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\nAPI server stopped")
    except Exception as e:
        print(f"Error starting API: {e}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Story Intelligence Dashboard - Backend Startup")
    print("=" * 60)
    print()
    
    if not check_requirements():
        print("\n⚠ Please fix the issues above before starting services")
        return 1
    
    print("\n" + "=" * 60)
    print("IMPORTANT: You need 3 terminals for full functionality:")
    print("=" * 60)
    print()
    print("Terminal 1 (this one): API Server")
    print("  python start_all.py")
    print()
    print("Terminal 2: Celery Worker")
    print("  celery -A celery_app worker --loglevel=info")
    print()
    print("Terminal 3: Celery Beat (Scheduler)")
    print("  celery -A celery_app beat --loglevel=info")
    print()
    print("=" * 60)
    print()
    
    response = input("Start API server now? (y/n): ").strip().lower()
    if response == 'y':
        start_api()
    else:
        print("Run 'python main.py' manually to start the API server")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
