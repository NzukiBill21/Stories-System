# Quick Start: Getting Data to Your Dashboard

## 🚀 5-Minute Setup

### Step 1: Database Setup (1 minute)
```bash
cd backend
python test_db_connection.py  # Should print "Database connected successfully"
python init_db.py             # Creates tables and adds sample sources
```

### Step 2: Configure API Keys (2 minutes)
Edit `backend/.env`:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=story_intelligence

TWITTER_BEARER_TOKEN=your_token_here
FACEBOOK_ACCESS_TOKEN=your_token_here
INSTAGRAM_ACCESS_TOKEN=your_token_here
```

### Step 3: Trigger First Scrape (1 minute)
```bash
python trigger_scrape.py
# Type 'y' when prompted
```

### Step 4: Verify Everything Works (1 minute)
```bash
python verify_data_flow.py
# Should show all checks passing
```

### Step 5: Start Services

**Terminal 1 - API:**
```bash
python main.py
```

**Terminal 2 - Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```bash
celery -A celery_app beat --loglevel=info
```

**Terminal 4 - Frontend:**
```bash
cd ..
npm run dev
```

Open `http://localhost:5173` - you should see stories!

## ✅ Verification Checklist

Run this to verify everything:
```bash
python verify_data_flow.py
```

You should see:
- ✓ Database connected successfully
- ✓ All tables exist
- ✓ Active sources configured
- ✓ Data in database (stories count > 0)
- ✓ Scraping activity logged
- ✓ Stories sorted by score (highest first)
- ✓ API endpoint working

## 📊 Understanding Content Hierarchy

**Stories are automatically sorted by score (highest first):**

1. **Database** - Stories stored with `score` field (0-100)
2. **API** - Returns stories ordered by `score DESC`
3. **Frontend** - Displays stories in API order

**Score Calculation:**
- 50% Engagement Velocity (likes/comments/shares per hour)
- 30% Source Credibility (trusted sources = higher)
- 20% Topic Relevance (trending keywords)

**Result:** Most important/highest-engagement stories appear first!

## 🔍 Troubleshooting

### No Stories Showing?
1. Check scraping ran: `python verify_data_flow.py`
2. Trigger manual scrape: `python trigger_scrape.py`
3. Check API keys in `.env`
4. Check scrape logs for errors

### Stories Not Sorted?
- API automatically sorts by score DESC
- Run `python verify_data_flow.py` section 8 to verify
- Check database: `SELECT id, score FROM stories ORDER BY score DESC`

### Scraping Not Running?
1. Check Celery worker is running
2. Check Celery beat is running
3. Check Redis is running: `redis-cli ping`
4. Verify sources are active

## 📈 Monitoring

**Check scraping activity:**
```bash
python verify_data_flow.py
# See section "5. SCRAPING ACTIVITY"
```

**Check API endpoint:**
```bash
curl http://localhost:8000/api/stories?limit=5
# Should return stories sorted by score
```

**View database directly:**
```sql
SELECT id, score, headline, platform 
FROM stories 
WHERE is_active = 1 
ORDER BY score DESC 
LIMIT 10;
```

## 🎯 Expected Behavior

- ✅ Stories appear on dashboard
- ✅ Stories sorted by importance (score)
- ✅ New stories every 15-30 minutes
- ✅ High-engagement stories prioritized
- ✅ Trusted sources get higher scores

## 📝 Next Steps

1. **Add more sources** - Monitor more accounts
2. **Adjust thresholds** - Filter content appropriately
3. **Configure trusted sources** - Boost credibility scores
4. **Set trending keywords** - Improve topic relevance

Your dashboard is now pulling data, saving it correctly, and displaying stories in proper hierarchy! 🎉
