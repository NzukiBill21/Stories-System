"""
Add Facebook Pages to database.

This script adds public Facebook Pages that will be used for trend aggregation.
Only Facebook Pages (not user profiles) are supported.

Example Pages:
- Kenyan Media: Citizen TV Kenya, NTV Kenya, Nation Media, TUKO
- Global Media: BBC News, CNN, Reuters
"""
from database import SessionLocal, test_connection
from models import Source
from loguru import logger
import sys


# Predefined Facebook Pages (Page IDs need to be obtained from Graph API Explorer)
KENYAN_MEDIA_PAGES = [
    {
        "account_handle": "citizentvkenya",
        "account_name": "Citizen TV Kenya",
        "account_id": None,  # TODO: Get from Graph API Explorer
        "is_trusted": True,
        "is_kenyan": True,
        "location": "Nairobi, Kenya"
    },
    {
        "account_handle": "ntvkenya",
        "account_name": "NTV Kenya",
        "account_id": None,  # TODO: Get from Graph API Explorer
        "is_trusted": True,
        "is_kenyan": True,
        "location": "Nairobi, Kenya"
    },
    {
        "account_handle": "nationmedia",
        "account_name": "Nation Media Group",
        "account_id": None,  # TODO: Get from Graph API Explorer
        "is_trusted": True,
        "is_kenyan": True,
        "location": "Nairobi, Kenya"
    },
    {
        "account_handle": "tukonews",
        "account_name": "TUKO News",
        "account_id": None,  # TODO: Get from Graph API Explorer
        "is_trusted": True,
        "is_kenyan": True,
        "location": "Nairobi, Kenya"
    },
]

GLOBAL_MEDIA_PAGES = [
    {
        "account_handle": "bbcnews",
        "account_name": "BBC News",
        "account_id": "228735667216",  # Known BBC News Page ID
        "is_trusted": True,
        "is_kenyan": False,
        "location": "London, UK"
    },
    {
        "account_handle": "cnn",
        "account_name": "CNN",
        "account_id": None,  # TODO: Get from Graph API Explorer
        "is_trusted": True,
        "is_kenyan": False,
        "location": "Atlanta, USA"
    },
]


def add_page(page_data: dict, db) -> bool:
    """Add a Facebook Page to database."""
    # Check if already exists
    existing = db.query(Source).filter(
        Source.platform == "Facebook",
        Source.account_handle == page_data["account_handle"]
    ).first()
    
    if existing:
        print(f"  [SKIP] {page_data['account_name']} already exists")
        return False
    
    # Create new source
    source = Source(
        platform="Facebook",
        account_handle=page_data["account_handle"],
        account_name=page_data["account_name"],
        account_id=page_data.get("account_id"),  # Page ID (required for Pages)
        is_active=True,
        is_trusted=page_data.get("is_trusted", False),
        is_kenyan=page_data.get("is_kenyan", False),
        location=page_data.get("location"),
        scrape_frequency_minutes=15
    )
    
    db.add(source)
    print(f"  [OK] Added {page_data['account_name']}")
    return True


def get_page_id_from_user(page_name: str) -> str:
    """Prompt user for Page ID."""
    print()
    print(f"To get Page ID for {page_name}:")
    print("  1. Go to: https://developers.facebook.com/tools/explorer/")
    print("  2. Query: GET /{page_username}")
    print("     Or search: GET /search?q={page_name}&type=page")
    print("  3. Copy the 'id' field")
    print()
    page_id = input(f"Enter Page ID for {page_name} (or press Enter to skip): ").strip()
    return page_id if page_id else None


def main():
    """Main function."""
    print("=" * 60)
    print("Add Facebook Pages for Trend Aggregation")
    print("=" * 60)
    print()
    print("This script adds public Facebook Pages to the database.")
    print("Only Facebook Pages (not user profiles) are supported.")
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    db = SessionLocal()
    try:
        added_count = 0
        
        # Add Kenyan media pages
        print("Kenyan Media Pages:")
        for page_data in KENYAN_MEDIA_PAGES:
            if not page_data.get("account_id"):
                # Try to get from user
                page_id = get_page_id_from_user(page_data["account_name"])
                if page_id:
                    page_data["account_id"] = page_id
                else:
                    print(f"  [SKIP] {page_data['account_name']} - no Page ID provided")
                    continue
            
            if add_page(page_data, db):
                added_count += 1
        
        print()
        
        # Add global media pages
        print("Global Media Pages:")
        for page_data in GLOBAL_MEDIA_PAGES:
            if not page_data.get("account_id"):
                # Try to get from user
                page_id = get_page_id_from_user(page_data["account_name"])
                if page_id:
                    page_data["account_id"] = page_id
                else:
                    print(f"  [SKIP] {page_data['account_name']} - no Page ID provided")
                    continue
            
            if add_page(page_data, db):
                added_count += 1
        
        db.commit()
        
        print()
        print("=" * 60)
        print(f"[OK] Added {added_count} Facebook Page(s)")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run: python scrape_facebook_trends.py")
        print("  2. This will aggregate trends from all Pages")
        print("  3. View dashboard to see trending stories")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        db.rollback()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
