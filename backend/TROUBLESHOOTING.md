# Troubleshooting Guide

## Dependency Conflict Error

### Problem
When installing requirements, you may encounter:
```
ERROR: Cannot install -r requirements.txt (line 2), -r requirements.txt (line 24), -r requirements.txt (line 5) and pydantic==2.5.3 because these package versions have conflicting dependencies.
```

### Cause
The `instagrapi==2.0.0` package requires Pydantic v1.x, while FastAPI 0.109.0+ requires Pydantic v2.x. This creates an incompatible dependency conflict.

### Solution
`instagrapi` has been removed from `requirements.txt` because:
1. The Instagram scraper uses the Instagram Graph API directly (via `requests`), not `instagrapi`
2. The Graph API approach is more reliable and doesn't have dependency conflicts
3. `instagrapi` is primarily for scraping without API access, which we don't need

### Installation Steps

1. **Update pip** (recommended):
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install requirements**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **If you still encounter issues**, try installing in a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Alternative: If You Need instagrapi

If you specifically need `instagrapi` for scraping (without API access), you have two options:

**Option 1: Use a separate environment**
Create a separate virtual environment for Instagram scraping with Pydantic v1:
```bash
python -m venv instagram_env
instagram_env\Scripts\activate  # Windows
pip install instagrapi==2.0.0 pydantic==1.10.13
```

**Option 2: Use instagrapi2 (if available)**
Check if there's a newer version that supports Pydantic v2:
```bash
pip install instagrapi2  # If available
```

### Current Instagram Implementation

The current Instagram scraper (`backend/platforms/instagram.py`) uses:
- **Instagram Graph API** (official API)
- **requests** library (no extra dependencies)
- Requires `INSTAGRAM_ACCESS_TOKEN` in `.env`

This is the recommended approach as it's:
- More reliable
- Officially supported
- No dependency conflicts
- Better rate limiting

### Other Common Issues

#### "Module not found" after installation
- Ensure you're in the correct directory
- Check if virtual environment is activated
- Try: `pip install -r requirements.txt --force-reinstall`

#### Database connection errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists: `createdb story_intelligence`

#### Redis connection errors
- Verify Redis is running: `redis-cli ping`
- Check `REDIS_URL` in `.env`

#### CORS errors in frontend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/api.py`
- Verify frontend URL matches allowed origins
