# Story Intelligence Dashboard - Project Summary

## Overview

A complete full-stack system for monitoring, scoring, and displaying high-engagement social media content across multiple platforms.

## Architecture

### Frontend (React + TypeScript + Vite)
- **Location**: Root directory
- **Port**: 5173 (default Vite port)
- **Framework**: React with TypeScript
- **UI Components**: Radix UI, Tailwind CSS, Motion animations
- **Features**:
  - Real-time story dashboard
  - Story filtering and search
  - Source management interface
  - Control panel for scraping
  - Insights and analytics

### Backend (Python + FastAPI)
- **Location**: `backend/` directory
- **Port**: 8000
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **Features**:
  - Multi-platform scraping (X/Twitter, Facebook, Instagram, TikTok)
  - Intelligent scoring system
  - High-engagement filtering
  - RESTful API
  - Scheduled scraping tasks

## Key Components

### Backend Structure

```
backend/
├── api.py                 # FastAPI application and endpoints
├── config.py              # Configuration and settings
├── database.py            # Database connection and session
├── models.py              # SQLAlchemy database models
├── scoring.py             # Scoring algorithms
├── services.py            # Business logic layer
├── celery_app.py          # Celery tasks and scheduling
├── main.py                # Application entry point
├── init_db.py             # Database initialization
├── platforms/             # Platform scrapers (modular)
│   ├── base.py            # Base scraper class
│   ├── twitter.py         # Twitter/X scraper
│   ├── facebook.py        # Facebook scraper
│   ├── instagram.py       # Instagram scraper
│   └── tiktok.py          # TikTok scraper (placeholder)
└── alembic/               # Database migrations
```

### Database Schema

1. **sources** - Social media accounts to monitor
   - Platform, handle, name, trust status
   - Scraping frequency configuration

2. **raw_posts** - Raw posts fetched from platforms
   - Platform-specific data
   - Engagement metrics (likes, comments, shares, views)
   - Timestamps and URLs

3. **stories** - Scored, filtered, normalized stories
   - Overall score and velocity
   - Credibility and topic relevance scores
   - Ready for dashboard display

### Scoring System

Posts are scored using a weighted algorithm:

1. **Engagement Velocity** (50% weight)
   - Calculates engagement per hour
   - Considers likes, comments, shares, views
   - Normalized to 0-100 scale

2. **Source Credibility** (30% weight)
   - Trusted source status
   - Predefined trusted accounts list
   - Default credibility for unknown sources

3. **Topic Relevance** (20% weight)
   - Trending keyword matching
   - Configurable keyword list
   - Content analysis

**Thresholds**:
- Minimum score: 50 (configurable)
- Minimum velocity: 10 engagement/hour (configurable)
- Only posts meeting both thresholds are kept

### API Endpoints

- `GET /api/stories` - Get trending stories (with filters)
- `GET /api/stories/{id}` - Get single story
- `POST /api/scrape/{source_id}` - Trigger manual scrape
- `GET /api/sources` - Get all active sources
- `GET /api/health` - Health check

### Platform Scrapers

Modular design allows easy addition of new platforms:

1. Inherit from `PlatformScraper` base class
2. Implement `fetch_posts()` method
3. Implement `normalize_post()` method
4. Register in `platforms/__init__.py`

**Supported Platforms**:
- ✅ X/Twitter (via Tweepy API)
- ✅ Facebook (via Graph API)
- ✅ Instagram (via Graph API)
- ⏳ TikTok (placeholder, requires API approval)

## Data Flow

```
1. Celery Beat triggers scheduled scraping
   ↓
2. Celery Worker executes scrape task
   ↓
3. Platform Scraper fetches posts from API
   ↓
4. Raw posts stored in database
   ↓
5. Scoring system processes each post
   ↓
6. High-scoring posts become "stories"
   ↓
7. Stories stored in normalized format
   ↓
8. Frontend fetches stories via REST API
   ↓
9. Dashboard displays trending stories
```

## Configuration

### Environment Variables

**Database**:
- `DATABASE_URL` - PostgreSQL connection string

**Redis**:
- `REDIS_URL` - Redis connection string

**API Keys** (required for scraping):
- `TWITTER_BEARER_TOKEN`, `TWITTER_API_KEY`, etc.
- `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, etc.
- `INSTAGRAM_ACCESS_TOKEN`

**Scoring**:
- `MIN_ENGAGEMENT_SCORE` - Minimum score threshold (default: 50)
- `MIN_ENGAGEMENT_VELOCITY` - Minimum velocity threshold (default: 10)

### Trusted Sources

Configure in `backend/config.py`:
```python
trusted_sources = [
    "@BBCNews",
    "@CNN",
    "@Reuters",
    # Add more...
]
```

### Trending Keywords

Configure in `backend/config.py`:
```python
trending_keywords = [
    "breaking",
    "election",
    "crisis",
    # Add more...
]
```

## Features

### ✅ Implemented

- Multi-platform scraping (X, Facebook, Instagram)
- Intelligent scoring system
- High-engagement filtering
- RESTful API with CORS
- Scheduled scraping via Celery
- Database models and migrations
- Error handling and rate limiting
- Frontend API integration
- Modular platform architecture

### 🔄 Future Enhancements

- TikTok API integration (requires approval)
- Real-time WebSocket updates
- Advanced analytics dashboard
- Source management UI
- Custom keyword monitoring
- Email/SMS alerts for high-priority stories
- Export functionality (CSV, JSON)
- User authentication and multi-tenancy

## Getting Started

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   # Configure .env file
   python init_db.py
   python main.py
   ```

2. **Frontend Setup**:
   ```bash
   npm install
   npm run dev
   ```

3. **Start Celery**:
   ```bash
   celery -A celery_app worker --loglevel=info
   celery -A celery_app beat --loglevel=info
   ```

See `SETUP.md` for detailed instructions.

## Testing

### Backend API
```bash
# Health check
curl http://localhost:8000/api/health

# Get stories
curl http://localhost:8000/api/stories

# API docs
open http://localhost:8000/docs
```

### Frontend
- Open `http://localhost:5173`
- Dashboard should display stories (or mock data if API unavailable)

## Project Status

✅ **Backend**: Complete and functional
✅ **Frontend Integration**: Complete
✅ **Database**: Schema defined and migrations ready
✅ **Scraping**: Multi-platform support implemented
✅ **Scoring**: Algorithm implemented and tested
✅ **API**: RESTful endpoints ready
✅ **Scheduling**: Celery tasks configured

## Notes

- **API Keys Required**: Social media APIs require developer accounts and API keys
- **Rate Limits**: All scrapers handle rate limits automatically
- **Public Data Only**: System only collects publicly available content
- **Modular Design**: Easy to add new platforms or modify scoring
- **Production Ready**: Includes error handling, logging, and monitoring hooks

## Support

- Backend README: `backend/README.md`
- Setup Guide: `SETUP.md`
- API Docs: `http://localhost:8000/docs` (when running)
