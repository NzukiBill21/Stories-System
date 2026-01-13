# Complete Data Flow Guide - Getting Data to Your Dashboard

This guide ensures your Story Intelligence Dashboard is pulling data, saving it correctly, and displaying it with proper hierarchy (sorted by score).

## Quick Start Checklist

Follow these steps in order:

### 1. ✅ Database Setup
```bash
cd backend
python test_db_connection.py
python init_db.py
```

### 2. ✅ Configure API Keys
Edit `backend/.env` and add your social media API keys:
- `TWITTER_BEARER_TOKEN` (required for X/Twitter)
- `FACEBOOK_ACCESS_TOKEN` (required for Facebook)
- `INSTAGRAM_ACCESS_TOKEN` (required for Instagram)

### 3. ✅ Verify Everything Works
```bash
python verify_data_flow.py
```

This will check:
- Database connection
- Tables exist
- Sources configured
- Data exists
- Scraping activity
- Story hierarchy (sorted by score)
- API endpoint

### 4. ✅ Trigger First Scrape
```bash
python trigger_scrape.py
```

This manually triggers scraping for all active sources.

### 5. ✅ Start Backend Services

**Terminal 1 - API Server:**
```bash
cd backend
python main.py
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

### 6. ✅ Start Frontend
```bash
npm run dev
```

Open `http://localhost:5173` - you should see stories!

## Understanding the Data Flow

### Step-by-Step Process

```
1. Celery Beat (Scheduler)
   ↓ (every 15 minutes)
2. Celery Worker
   ↓ (triggers scrape task)
3. Platform Scraper (Twitter/Facebook/Instagram)
   ↓ (fetches posts via API)
4. Raw Posts → Database (raw_posts table)
   ↓
5. Scoring System
   - Calculates engagement velocity
   - Checks source credibility
   - Matches trending keywords
   ↓
6. Filtering (only high-engagement posts)
   ↓
7. Stories → Database (stories table, sorted by score)
   ↓
8. API Endpoint (/api/stories)
   ↓ (returns JSON sorted by score DESC)
9. Frontend Dashboard
   ↓ (displays stories in order)
10. User sees content hierarchy!
```

## Ensuring Proper Content Hierarchy

### How Stories Are Sorted

Stories are **automatically sorted by score** (highest first) at multiple levels:

1. **Database Query** (`services.py`):
   ```python
   query = query.order_by(Story.score.desc())
   ```

2. **API Response** (`api.py`):
   - Returns stories in the order from database (already sorted)

3. **Frontend Display** (`Dashboard.tsx`):
   - Displays stories in the order received from API

### Score Calculation

Each story gets a score (0-100) based on:

- **50%** - Engagement Velocity (likes/comments/shares per hour)
- **30%** - Source Credibility (trusted sources get higher scores)
- **20%** - Topic Relevance (trending keyword matches)

**Higher score = Higher priority = Shown first**

### Verifying Hierarchy

Run the verification script:
```bash
python verify_data_flow.py
```

Look for section "8. STORY HIERARCHY VERIFICATION" - it will show:
- Stories sorted by score (highest to lowest)
- Each story's score, velocity, and engagement metrics
- Confirmation that sorting is correct

## Troubleshooting

### No Data Showing on Dashboard

1. **Check if scraping has run:**
   ```bash
   python verify_data_flow.py
   ```
   Look at "4. DATA IN DATABASE" section

2. **Check scraping logs:**
   ```bash
   # In Python shell
   from database import SessionLocal
   from models import ScrapeLog
   db = SessionLocal()
   logs = db.query(ScrapeLog).order_by(ScrapeLog.started_at.desc()).limit(5).all()
   for log in logs:
       print(f"{log.status}: {log.posts_fetched} posts, {log.stories_created} stories")
   ```

3. **Trigger manual scrape:**
   ```bash
   python trigger_scrape.py
   ```

4. **Check API keys:**
   - Verify API keys are in `.env` file
   - Test API access manually
   - Check for rate limit errors in logs

### Stories Not Sorted Correctly

1. **Verify API endpoint:**
   ```bash
   curl http://localhost:8000/api/stories?limit=5
   ```
   Stories should be in descending score order

2. **Check database directly:**
   ```sql
   SELECT id, score, headline FROM stories 
   WHERE is_active = 1 
   ORDER BY score DESC 
   LIMIT 10;
   ```

3. **Run hierarchy verification:**
   ```bash
   python verify_data_flow.py
   ```
   Section 8 will show if sorting is correct

### Low Engagement Stories Showing

Adjust scoring thresholds in `backend/.env`:
```env
MIN_ENGAGEMENT_SCORE=50      # Minimum score (0-100)
MIN_ENGAGEMENT_VELOCITY=10   # Minimum engagement per hour
```

Higher values = only very high-engagement stories shown

### Scraping Not Running Automatically

1. **Check Celery Beat is running:**
   ```bash
   # Should see scheduled tasks
   celery -A celery_app beat --loglevel=info
   ```

2. **Check Celery Worker is running:**
   ```bash
   # Should process tasks
   celery -A celery_app worker --loglevel=info
   ```

3. **Check Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

4. **Verify sources are active:**
   ```bash
   python verify_data_flow.py
   ```
   Check "3. SOURCES CONFIGURATION" section

## Monitoring Data Flow

### Check What's Happening

1. **View recent scraping activity:**
   ```bash
   python verify_data_flow.py
   ```
   See section "5. SCRAPING ACTIVITY"

2. **Check database stats:**
   ```sql
   SELECT 
     COUNT(*) as total_stories,
     AVG(score) as avg_score,
     MAX(score) as max_score,
     COUNT(*) FILTER (WHERE is_active = true) as active_stories
   FROM stories;
   ```

3. **Monitor API endpoint:**
   ```bash
   watch -n 5 'curl -s http://localhost:8000/api/stories?limit=1 | jq ".[0] | {score: .credibility, headline}"'
   ```

### Expected Behavior

- **Every 15 minutes**: Celery Beat triggers scraping
- **Within 1-2 minutes**: New posts appear in database
- **Immediately**: Stories are scored and filtered
- **Within 5 minutes**: Frontend refreshes and shows new stories
- **Stories sorted**: Highest score first, lowest score last

## Advanced Configuration

### Adjust Scraping Frequency

Edit sources in database:
```python
from database import SessionLocal
from models import Source

db = SessionLocal()
source = db.query(Source).filter(Source.id == 1).first()
source.scrape_frequency_minutes = 30  # Change to 30 minutes
db.commit()
```

### Add More Sources

```python
from database import SessionLocal
from models import Source

db = SessionLocal()
new_source = Source(
    platform="X",
    account_handle="@YourAccount",
    account_name="Your Account Name",
    is_active=True,
    is_trusted=False,
    scrape_frequency_minutes=15
)
db.add(new_source)
db.commit()
```

### Customize Scoring

Edit `backend/config.py`:
- `trusted_sources` - List of high-credibility accounts
- `trending_keywords` - Keywords that boost relevance score
- `min_engagement_score` - Minimum score threshold
- `min_engagement_velocity` - Minimum velocity threshold

## Quick Verification Commands

```bash
# Test database connection
python test_db_connection.py

# Verify entire system
python verify_data_flow.py

# Trigger manual scrape
python trigger_scrape.py

# Check API endpoint
curl http://localhost:8000/api/stories?limit=5

# Check health
curl http://localhost:8000/api/health
```

## Success Indicators

You'll know everything is working when:

1. ✅ `verify_data_flow.py` shows all checks passing
2. ✅ Dashboard shows stories (not just mock data)
3. ✅ Stories are sorted by importance (highest score first)
4. ✅ New stories appear every 15-30 minutes
5. ✅ Scrape logs show successful scraping
6. ✅ API returns stories in correct order

## Next Steps

Once data is flowing:

1. **Monitor scrape logs** to ensure consistent data collection
2. **Adjust scoring thresholds** to filter content appropriately
3. **Add more sources** to monitor more accounts
4. **Configure trusted sources** for better credibility scoring
5. **Set up trending keywords** for topic relevance

Your dashboard should now be pulling data, saving it correctly, and displaying stories in proper hierarchy (highest score first)!
