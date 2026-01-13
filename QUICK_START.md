# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python
python --version  # Should be 3.9+

# Check Node.js
node --version  # Should be 18+

# Check PostgreSQL
psql --version

# Check Redis
redis-cli ping  # Should return PONG
```

## 1. Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example and fill in your API keys)
# At minimum, set DATABASE_URL and REDIS_URL

# Initialize database
python init_db.py

# Start API server
python main.py
```

Backend API will be at `http://localhost:8000`

## 2. Start Celery (1 minute)

Open a new terminal:

```bash
cd backend

# Terminal 1: Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 2: Celery Beat (scheduler)
celery -A celery_app beat --loglevel=info
```

## 3. Frontend Setup (1 minute)

Open a new terminal:

```bash
# From project root
npm install
npm run dev
```

Frontend will be at `http://localhost:5173`

## 4. Verify Everything Works

1. **Check Backend**: Open `http://localhost:8000/docs` - should see API docs
2. **Check Frontend**: Open `http://localhost:5173` - should see dashboard
3. **Check API**: `curl http://localhost:8000/api/health` - should return `{"status": "healthy"}`

## Adding Your First Source

```python
# In Python shell or script
from database import SessionLocal
from models import Source

db = SessionLocal()
source = Source(
    platform="X",
    account_handle="@BBCNews",  # Your target account
    account_name="BBC News",
    is_active=True,
    is_trusted=True,
    scrape_frequency_minutes=15
)
db.add(source)
db.commit()
```

Then trigger a scrape:
```bash
curl -X POST http://localhost:8000/api/scrape/1
```

## Common Issues

**"Module not found"**: Run `pip install -r requirements.txt` again

**"Database connection failed"**: Check PostgreSQL is running and DATABASE_URL is correct

**"Redis connection failed"**: Check Redis is running and REDIS_URL is correct

**"No stories showing"**: 
- Check sources exist: `curl http://localhost:8000/api/sources`
- Trigger manual scrape: `curl -X POST http://localhost:8000/api/scrape/1`
- Check Celery worker logs for errors

**"CORS errors"**: Backend CORS is configured for `localhost:5173` - check your frontend URL matches

## Next Steps

1. Add more sources to monitor
2. Configure trusted sources in `backend/config.py`
3. Add trending keywords in `backend/config.py`
4. Adjust scoring thresholds in `.env`
5. Set up API keys for social media platforms

## Need Help?

- Full setup: See `SETUP.md`
- Project overview: See `PROJECT_SUMMARY.md`
- Backend docs: See `backend/README.md`
- API docs: `http://localhost:8000/docs`
