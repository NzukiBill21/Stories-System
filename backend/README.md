# Story Intelligence Dashboard - Python Backend

Backend system for pulling, scoring, and serving social media content for the Story Intelligence Dashboard.

## Features

- **Multi-platform scraping**: X/Twitter, Facebook, Instagram, TikTok (modular design)
- **Intelligent scoring**: Engagement velocity, source credibility, trending keywords
- **High-engagement filtering**: Only keeps posts that meet engagement thresholds
- **RESTful API**: FastAPI endpoints for frontend integration
- **Scheduled scraping**: Celery tasks for automated content collection
- **PostgreSQL storage**: Structured database with normalized data

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis (for Celery)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

3. Set up the database:
```bash
# Create database
createdb story_intelligence

# Run migrations
alembic upgrade head
```

4. Add initial sources (example):
```python
from database import SessionLocal
from models import Source

db = SessionLocal()
source = Source(
    platform="X",
    account_handle="@BBCNews",
    account_name="BBC News",
    is_active=True,
    is_trusted=True,
    scrape_frequency_minutes=15
)
db.add(source)
db.commit()
```

## Running

### API Server

```bash
python main.py
# or
uvicorn api:app --reload
```

API will be available at `http://localhost:8000`

### Celery Worker

```bash
celery -A celery_app worker --loglevel=info
```

### Celery Beat (Scheduler)

```bash
celery -A celery_app beat --loglevel=info
```

## API Endpoints

### Get Trending Stories
```
GET /api/stories?limit=50&min_score=50&platform=X&hours_back=24
```

### Get Single Story
```
GET /api/stories/{story_id}
```

### Trigger Scraping
```
POST /api/scrape/{source_id}
```

### Get Sources
```
GET /api/sources
```

### Health Check
```
GET /api/health
```

## Configuration

Edit `config.py` or set environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `TWITTER_BEARER_TOKEN`: Twitter API bearer token
- `FACEBOOK_ACCESS_TOKEN`: Facebook API access token
- `INSTAGRAM_ACCESS_TOKEN`: Instagram API access token
- `MIN_ENGAGEMENT_SCORE`: Minimum score to keep a post (default: 50)
- `MIN_ENGAGEMENT_VELOCITY`: Minimum engagement/hour (default: 10)

## Architecture

### Database Schema

- **sources**: Social media accounts to monitor
- **raw_posts**: Raw posts fetched from platforms
- **stories**: Scored, filtered, normalized stories ready for dashboard

### Scoring System

Posts are scored based on:
1. **Engagement Velocity** (50% weight): Likes/comments/shares per hour
2. **Source Credibility** (30% weight): Trusted source status
3. **Topic Relevance** (20% weight): Trending keyword matches

Only posts meeting `MIN_ENGAGEMENT_SCORE` and `MIN_ENGAGEMENT_VELOCITY` thresholds are kept.

### Platform Scrapers

Modular design allows easy addition of new platforms:
1. Create scraper class inheriting from `PlatformScraper`
2. Implement `fetch_posts()` and `normalize_post()` methods
3. Register in `platforms/__init__.py`

## Development

### Adding a New Platform

1. Create `backend/platforms/newplatform.py`:
```python
from platforms.base import PlatformScraper

class NewPlatformScraper(PlatformScraper):
    def __init__(self):
        super().__init__("NewPlatform")
    
    def fetch_posts(self, source, limit=50):
        # Implementation
        pass
    
    def normalize_post(self, raw_data, source):
        # Normalize to standard format
        pass
```

2. Register in `platforms/__init__.py`

3. Update `models.py` Source.platform choices if needed

## Notes

- **Rate Limiting**: All scrapers handle rate limits automatically
- **Error Handling**: Failed scrapes are logged but don't crash the system
- **Data Privacy**: Only public data is collected (no private posts)
- **API Keys**: Required for official APIs (Twitter, Facebook, Instagram)
