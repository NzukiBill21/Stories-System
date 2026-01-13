# TikTok Scraper - Quick Start

## Installation (2 minutes)

```bash
cd backend
pip install TikTokApi playwright

# On Windows:
python -m playwright install chromium

# On Linux/Mac:
playwright install chromium
```

## Test the Scraper

```bash
python test_tiktok_scraper.py
```

Should output:
```
✓ Database connected
✓ Scraper initialized
✓ Fetched X videos
```

## Add TikTok Source

The scraper is already included in `init_db.py`, but you can add manually:

```python
from database import SessionLocal
from models import Source

db = SessionLocal()
tiktok_source = Source(
    platform="TikTok",
    account_handle="trending",
    account_name="TikTok Trending",
    is_active=True,
    scrape_frequency_minutes=30
)
db.add(tiktok_source)
db.commit()
```

## Configure Threshold

Edit `backend/.env`:

```env
TIKTOK_MIN_ENGAGEMENT_VELOCITY=100  # Minimum engagement per minute
```

- **Lower** (50) = More videos kept
- **Higher** (200) = Only very high engagement

## Trigger Scraping

```bash
python trigger_scrape.py
```

Or wait for automatic scraping (every 15-30 minutes via Celery).

## Verify in Dashboard

1. Start API: `python main.py`
2. Start frontend: `npm run dev`
3. Open `http://localhost:5173`
4. TikTok stories should appear!

## Troubleshooting

**"TikTokApi not installed"**
```bash
pip install TikTokApi playwright
playwright install chromium
```

**"No videos fetched"**
- Check internet connection
- Lower `TIKTOK_MIN_ENGAGEMENT_VELOCITY` threshold
- TikTok may be blocking (try later)

**"All videos filtered out"**
- Videos don't meet engagement threshold
- Lower threshold or check if videos are actually trending

See `TIKTOK_SETUP.md` for detailed documentation.
