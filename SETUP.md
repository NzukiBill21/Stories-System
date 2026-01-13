# Story Intelligence Dashboard - Setup Guide

Complete setup guide for both frontend and backend.

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL 12+
- Redis (for Celery task queue)

## Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

```bash
# Create database
createdb story_intelligence

# Or using psql:
psql -U postgres
CREATE DATABASE story_intelligence;
```

### 3. Configure Environment Variables

Create `backend/.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/story_intelligence
REDIS_URL=redis://localhost:6379/0

# Twitter/X API (get from https://developer.twitter.com/)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Facebook API (get from https://developers.facebook.com/)
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token

# Instagram API (get from https://developers.facebook.com/docs/instagram-api/)
INSTAGRAM_ACCESS_TOKEN=your_instagram_token

# Optional: Adjust thresholds
MIN_ENGAGEMENT_SCORE=50
MIN_ENGAGEMENT_VELOCITY=10.0
```

### 4. Initialize Database

```bash
cd backend
python init_db.py
```

This creates the database tables and adds sample sources.

### 5. Run Database Migrations (Optional)

If you want to use Alembic for migrations:

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Start Backend Services

**Terminal 1 - API Server:**
```bash
cd backend
python main.py
# API will be available at http://localhost:8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
cd backend
celery -A celery_app beat --loglevel=info
```

## Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure API URL (Optional)

Create `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

### 3. Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173` (or the port Vite assigns).

## Testing the Setup

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
```

### 2. Check API Endpoints

```bash
# Get stories
curl http://localhost:8000/api/stories

# Get sources
curl http://localhost:8000/api/sources

# Trigger manual scrape (replace 1 with actual source ID)
curl -X POST http://localhost:8000/api/scrape/1
```

### 3. View API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Adding Social Media Sources

### Via Python Script

```python
from database import SessionLocal
from models import Source

db = SessionLocal()
source = Source(
    platform="X",  # or "Facebook", "Instagram", "TikTok"
    account_handle="@username",  # Without @ for Facebook/Instagram
    account_name="Display Name",
    is_active=True,
    is_trusted=False,  # Set True for verified/trusted sources
    scrape_frequency_minutes=15  # How often to check (15, 30, 60, etc.)
)
db.add(source)
db.commit()
```

### Via API (Future Enhancement)

You can add an endpoint to add sources via API if needed.

## Troubleshooting

### Backend Issues

1. **Database Connection Error**
   - Check PostgreSQL is running: `pg_isready`
   - Verify DATABASE_URL in `.env` is correct
   - Ensure database exists: `psql -l | grep story_intelligence`

2. **Redis Connection Error**
   - Check Redis is running: `redis-cli ping`
   - Verify REDIS_URL in `.env` is correct

3. **API Key Errors**
   - Verify API keys are correctly set in `.env`
   - Check API key permissions and rate limits
   - Some platforms require app approval before production use

4. **Import Errors**
   - Ensure you're in the `backend` directory
   - Check Python path: `python -c "import sys; print(sys.path)"`
   - Install missing packages: `pip install -r requirements.txt`

### Frontend Issues

1. **CORS Errors**
   - Ensure backend CORS is configured for your frontend URL
   - Check `backend/api.py` CORS settings

2. **API Connection Failed**
   - Verify backend is running on port 8000
   - Check `VITE_API_URL` in `.env` matches backend URL
   - Check browser console for errors

3. **No Stories Displayed**
   - Check backend has stories in database
   - Verify scraping tasks are running
   - Check Celery worker logs for errors

## Production Deployment

### Backend

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up proper environment variables
3. Use a production database (managed PostgreSQL)
4. Set up Redis for Celery
5. Configure proper logging
6. Set up monitoring and alerts

### Frontend

1. Build for production: `npm run build`
2. Serve static files with Nginx or similar
3. Configure API URL for production backend
4. Set up CDN for assets (optional)

## Architecture Overview

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│  (Port 5173)│
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│  FastAPI    │ (Python)
│  (Port 8000)│
└──────┬──────┘
       │
       ├──► PostgreSQL (Database)
       │
       └──► Redis ──► Celery Workers
                      │
                      ├──► Twitter/X API
                      ├──► Facebook API
                      ├──► Instagram API
                      └──► TikTok API (future)
```

## Next Steps

1. Add more trusted sources to monitor
2. Configure trending keywords in `backend/config.py`
3. Adjust scoring thresholds based on your needs
4. Set up monitoring and alerting
5. Add more platforms as needed

## Support

For issues or questions, check:
- Backend README: `backend/README.md`
- API Documentation: `http://localhost:8000/docs`
- Logs: Check Celery worker and API server console output
