"""Create test data so dashboard shows something while we fix scraping."""
from database import SessionLocal, test_connection
from models import Source, RawPost, Story
from datetime import datetime, timedelta
from loguru import logger
import sys

def create_test_stories():
    """Create test stories from real sources."""
    print("=" * 60)
    print("Create Test Stories from Real Sources")
    print("=" * 60)
    print()
    
    if not test_connection():
        print("[ERROR] Database connection failed")
        return 1
    
    print("[OK] Database connected\n")
    
    db = SessionLocal()
    try:
        # Get active sources
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        if not sources:
            print("[ERROR] No active sources found")
            return 1
        
        print(f"Found {len(sources)} active source(s)\n")
        
        # Create test stories for each source
        stories_created = 0
        
        for source in sources:
            print(f"Creating test story for {source.platform} ({source.account_name})...")
            
            # Create realistic content based on platform
            if source.platform == "TikTok":
                content = "Breaking: Major tech company announces revolutionary AI breakthrough that could change everything. Industry experts are calling this a game-changer. #TechNews #AI #Innovation"
                headline = "Tech Company Announces Revolutionary AI Breakthrough"
            elif source.platform == "Facebook":
                content = "Breaking news: Major policy announcement expected today. Sources close to the matter say this could impact millions. Stay tuned for updates. #BreakingNews #Politics"
                headline = "Major Policy Announcement Expected Today"
            else:
                content = f"Trending story from {source.platform} - High engagement content that's going viral. This story is getting significant attention across social media platforms."
                headline = f"Trending Story from {source.platform}"
            
            # Create a raw post
            raw_post = RawPost(
                source_id=source.id,
                platform_post_id=f"test_{source.platform}_{datetime.now().timestamp()}",
                platform=source.platform,
                author=source.account_name or source.account_handle,
                content=content,
                url=f"https://{source.platform.lower()}.com/test/{datetime.now().timestamp()}",
                posted_at=datetime.utcnow() - timedelta(minutes=30),
                likes=1500,
                comments=250,
                shares=180,
                views=5000 if source.platform == "TikTok" else 0,
                raw_data="{}"
            )
            db.add(raw_post)
            db.flush()
            
            # Create story from raw post
            story = Story(
                raw_post_id=raw_post.id,
                platform=source.platform,
                author=source.account_name or source.account_handle,
                content=raw_post.content,
                url=raw_post.url,
                posted_at=raw_post.posted_at,
                likes=raw_post.likes,
                comments=raw_post.comments,
                shares=raw_post.shares,
                views=raw_post.views,
                engagement_velocity=120.5,  # High engagement
                credibility_score=85.0,
                topic_relevance_score=75.0,
                score=88.5,
                reason_flagged="High engagement velocity, trending content",
                headline=headline,
                is_active=True,
                is_kenyan=False
            )
            db.add(story)
            stories_created += 1
            print(f"  [OK] Created test story (Score: {story.score:.1f})")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"\nTest stories created: {stories_created}")
        print(f"Total stories in database: {db.query(Story).count()}")
        
        print("\n[OK] Test data created!")
        print("Dashboard should now show stories.")
        print("\nNote: These are test stories. Real scraping will replace them.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(create_test_stories())
