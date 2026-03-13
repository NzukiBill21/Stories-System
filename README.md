# Story Intelligence Dashboard

A full-stack system for monitoring, scoring, and displaying high-engagement social media content across multiple platforms. **Designed to catch hot stories for Kenya before they blow up.**

---

## Table of Contents

- [Overview](#-overview)
- [Languages Used](#-languages-used)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Data Flow](#-data-flow)
- [Scoring Algorithm](#-scoring-algorithm)
- [Kenyan Content](#-kenyan-content)
- [Development](#-development)
- [Further Documentation](#-further-documentation)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

The Story Intelligence Dashboard:

- **Scrapes content** from multiple social media platforms (X/Twitter, Facebook, Instagram, TikTok, Reddit, RSS, Google Trends, YouTube)
- **Scores and filters** posts by engagement velocity, credibility, and topic relevance
- **Prioritizes Kenyan content** with lower thresholds for early trend detection
- **Displays trending stories** in a real-time dashboard
- **Detects hot/emerging stories** before they go viral

---

## Languages Used

| Area | Languages & Technologies |
|------|--------------------------|
| **Backend** | Python 3.9+ |
| **API** | FastAPI (Python) |
| **Frontend** | TypeScript, TSX (React) |
| **Database** | SQL (MySQL / MariaDB) |
| **Styling** | CSS, Tailwind CSS |
| **Data/config** | JSON, YAML, `.env` |
| **Scripts** | Python, Shell (Bash) |

---

## ✨ Key Features

### 🔥 Hot Stories Detection

- **Early trend detection** – Catch stories before they blow up
- **High engagement velocity** – Only shows stories trending now
- **Kenyan-focused** – Lower thresholds for Kenyan content (30% lower score, 50% lower velocity)
- **Real-time updates** – Auto-refresh every 2 minutes when hot filter is on
- **Dedicated endpoint** – `GET /api/stories/hot`

### 🇰🇪 Kenyan Content Focus

- Kenyan source prioritization and location-based filtering (Nairobi, Mombasa, etc.)
- Kenyan keyword detection and lower thresholds to catch trends earlier
- Multiple Kenyan sources: RSS, Reddit, Google Trends, social media

### 📊 Scoring System

- **Engagement velocity** (50%) – Engagement per hour
- **Source credibility** (30%) – Trusted source verification
- **Topic relevance** (20%) – Trending keyword matching
- **Kenyan boost** – +15 for Kenyan content, +10 for Kenyan locations

### 🌐 Multi-Platform Support

| Platform      | Method                    |
|---------------|---------------------------|
| X/Twitter     | Tweepy API                |
| Facebook      | Graph API (Page-based)    |
| Instagram     | Graph API                 |
| TikTok        | Trending / hashtag        |
| Reddit        | r/Kenya, r/Nairobi, etc.  |
| RSS           | Kenyan news feeds         |
| Google Trends | Playwright scraping       |
| YouTube       | Video monitoring          |

### 🎨 Frontend

- **React 18 + TypeScript** – Type-safe UI
- **Vite** – Build and dev server
- **Tailwind CSS** – Styling
- **Radix UI + Motion** – Components and animations
- **Views:** Dashboard, Story detail, Filter panel, Sources management, Insights, Control panel
- **Filters:** Platform, velocity, credibility, Kenyan-only, hot stories, topic
- **Dark/light theme**, responsive layout

---

## 🏗️ Architecture

### Tech Stack

| Layer    | Technologies |
|----------|--------------|
| **Backend**  | FastAPI, SQLAlchemy, MySQL (e.g. XAMPP), optional Celery + Redis |
| **Scheduler**| Built-in `BackgroundScheduler` (thread-based, runs with API) |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Radix UI, Motion |

The backend runs a **built-in background scheduler** when the API starts. It checks active sources by `scrape_frequency_minutes` and triggers scrapes. **No Redis or Celery is required** for normal operation. Celery is available for optional distributed task queues.

### Project Structure

```
Stories-System/
├── backend/                      # Python FastAPI backend
│   ├── api.py                    # FastAPI app, CORS, REST endpoints
│   ├── main.py                   # Entry point (uvicorn)
│   ├── config.py                 # Settings from .env
│   ├── database.py               # SQLAlchemy engine, session
│   ├── models.py                 # Source, RawPost, Story, Hashtag, etc.
│   ├── services.py               # get_trending_stories, scrape_source, etc.
│   ├── scoring.py                # Engagement velocity & score calculation
│   ├── background_scheduler.py   # Auto-scraping (runs with API)
│   ├── hashtag_scraper.py        # Hashtag-based scraping
│   ├── celery_app.py             # Optional Celery app
│   ├── schema.sql                 # SQL schema (run with mysql)
│   ├── init_db.py                 # Create tables + sample sources (Python)
│   ├── init_kenyan_sources.py     # Seed Kenyan sources
│   ├── create_env_file.py         # Help creating .env
│   ├── platforms/                # Platform scrapers
│   │   ├── base.py               # Base scraper interface
│   │   ├── twitter.py
│   │   ├── facebook.py
│   │   ├── instagram.py
│   │   ├── tiktok.py
│   │   ├── reddit.py
│   │   ├── rss.py
│   │   ├── google_trends.py
│   │   └── youtube.py
│   ├── requirements.txt
│   └── *.md                      # Backend guides (MySQL, Kenyan, etc.)
├── src/                          # React frontend
│   ├── main.tsx
│   ├── app/
│   │   ├── App.tsx               # Root, theme, filters, API fetch
│   │   └── components/
│   │       ├── Dashboard.tsx     # Story grid
│   │       ├── StoryCard.tsx     # Single story card
│   │       ├── StoryDetailView.tsx
│   │       ├── FilterPanel.tsx   # Platform, velocity, hot, Kenyan, topic
│   │       ├── Sidebar.tsx
│   │       ├── ControlPanel.tsx
│   │       ├── SourcesManagement.tsx
│   │       ├── InsightsPanel.tsx
│   │       └── ui/               # Radix-based UI components
│   └── services/
│       └── api.ts                # fetchStories, fetchHotStories, fetchSources, etc.
├── package.json
└── README.md                     # This file
```

---

## Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **MySQL** (e.g. XAMPP or standalone)
- **Redis** (only if using Celery; not required for default setup)

---

## Installation

1. **Clone and enter the project**
   ```bash
   git clone <repository-url>
   cd Stories-System
   ```

2. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
   For Google Trends (Playwright):  
   `playwright install chromium`

3. **Environment**
   - Copy or create `backend/.env` (see [Configuration](#-configuration)).
   - Or run `python create_env_file.py` in `backend/` for a template.

4. **Database**
   - Start MySQL. Use one of these options:
     - **Option A (SQL file):** `mysql -u root -p < backend/schema.sql`
     - **Option B (Python):** `cd backend && python init_db.py` (creates tables from models, adds sample sources)
   - Set in `backend/.env`: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

5. **Initialize DB**
   ```bash
   # Option A: Run schema SQL (creates tables only)
   mysql -u root -p < backend/schema.sql

   # Option B: Use Python (creates tables + sample sources)
   cd backend
   python init_db.py
   ```
   Optional: `python init_kenyan_sources.py` for Kenyan sources.

6. **Frontend**
   ```bash
   npm install
   ```
   Optional: set `VITE_API_URL` (default `http://localhost:8000`) if your API runs elsewhere.

---

## Running the System

1. **Backend API (includes built-in scheduler)**
   ```bash
   cd backend
   python main.py
   ```
   API and scheduler run together. Default port is set in `config.py` (e.g. 8001); override with `API_PORT` in `.env`.

2. **Frontend**
   ```bash
   npm run dev
   ```
   Usually at `http://localhost:5173`.

3. **Optional: Celery worker + beat** (only if using Celery)
   ```bash
   cd backend
   celery -A celery_app worker --loglevel=info
   celery -A celery_app beat --loglevel=info
   ```

---

## 📡 API Reference

Base URL: `http://localhost:<API_PORT>` (e.g. 8000 or 8001).

### Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stories` | Trending stories. Query: `limit`, `hours_back`, `platform`, `is_kenyan`, `min_score`, `topic` |
| GET | `/api/stories/hot` | Hot/emerging stories. Query: `limit`, `is_kenyan`, `hours_back` (default 6) |
| GET | `/api/stories/{story_id}` | Single story by ID |

### Sources & Scraping

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sources` | List active sources. Query: `is_kenyan` |
| POST | `/api/scrape/{source_id}` | Trigger scrape for a source |
| POST | `/api/scrape/facebook-trends` | Aggregate Facebook trends. Query: `posts_per_page`, `top_n`, `min_trend_score` |

### Hashtags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hashtags` | List active hashtags. Query: `is_kenyan` |
| POST | `/api/scrape/hashtag/{hashtag_id}` | Trigger scrape for a hashtag |

### Analytics & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/insights` | Insights (velocity distribution, topics, platforms, keywords). Query: `hours_back` |
| GET | `/api/health` | Health check |
| GET | `/api/scheduler/status` | Scheduler status |

---

## ⚙️ Configuration

### Backend environment (`backend/.env`)

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=story_intelligence

# Server
API_HOST=0.0.0.0
API_PORT=8001

# Redis (only if using Celery)
REDIS_URL=redis://localhost:6379/0

# Platform API keys (optional)
TWITTER_BEARER_TOKEN=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_ACCESS_TOKEN=...
INSTAGRAM_ACCESS_TOKEN=...

# Scoring
MIN_ENGAGEMENT_SCORE=30
MIN_ENGAGEMENT_VELOCITY=5.0
```

### Frontend

- `VITE_API_URL` – Backend base URL (default `http://localhost:8000`). Must match your `API_PORT` if local.

### Scoring thresholds

- **Default:** `MIN_ENGAGEMENT_SCORE=30`, `MIN_ENGAGEMENT_VELOCITY=5.0` (per hour).
- **Kenyan:** Score threshold 30% lower (e.g. 21), velocity 50% lower (e.g. 2.5/hour).

---

## 📊 Data Flow

1. **Scheduler** (built-in or Celery) runs on an interval; each source has `scrape_frequency_minutes`.
2. **Platform scrapers** fetch posts; raw data is stored in `raw_posts`.
3. **Scoring** computes engagement velocity, credibility, topic relevance, and Kenyan boost; high-scoring posts become rows in `stories`.
4. **Frontend** calls `/api/stories` or `/api/stories/hot` (and other endpoints) and renders the dashboard with filters (platform, velocity, credibility, Kenyan-only, hot, topic).

---

## 📈 Scoring Algorithm

- **Engagement velocity:**  
  `(likes + comments*2 + shares*3 + views*0.1) / hours_since_posted`
- **Overall score:**  
  `(normalized_velocity * 0.5) + (credibility * 0.3) + (topic_relevance * 0.2) + kenyan_boost (+15) + location_boost (+10)`
- **Hot stories:**  
  `engagement_velocity >= 20.0`, `posted_at` within last N hours (e.g. 6), ordered by velocity descending.

---

## 🇰🇪 Kenyan Content

- **RSS:** Nation, Standard, Citizen TV, Tuko, The Star, Business Daily, Kenyans.co.ke, etc.
- **Social:** Reddit (r/Kenya, r/Nairobi), Google Trends Kenya, Facebook/Instagram/X Kenyan pages.
- **Hashtags:** e.g. #KenyaElections, #Nairobi, #Kenya. See `backend/init_kenyan_sources.py` and `kenyan_sources_config.py`.

---

## 🔧 Development

### Adding a platform scraper

1. Add `backend/platforms/new_platform.py` extending `PlatformScraper` from `platforms.base`: implement `fetch_posts`, `normalize_post`.
2. Register in `backend/platforms/__init__.py`.
3. Add the platform to the frontend `Story` platform type in `src/services/api.ts` (and any filters).

### Database migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 📚 Further Documentation

Backend docs in `backend/`:

- `MYSQL_SETUP.md`, `DATABASE_FIX_GUIDE.md` – Database setup and fixes
- `KENYAN_SETUP_GUIDE.md`, `KENYAN_IMPLEMENTATION_SUMMARY.md` – Kenyan sources and config
- `FACEBOOK_INSTAGRAM_SETUP.md`, `INSTAGRAM_*.md`, `TIKTOK_SETUP.md` – Platform setup
- `TROUBLESHOOTING.md` – Common issues

---

## 🐛 Troubleshooting

| Issue | Checks |
|-------|--------|
| Backend won’t start | MySQL running; `.env` DB_* correct; port free |
| No stories | Scheduler running (start API with `main.py`); sources active; try lowering credibility filter |
| CORS errors | Allowed origins in `backend/api.py` include your frontend origin (e.g. `http://localhost:5173`) |
| Frontend can’t reach API | `VITE_API_URL` matches backend host and `API_PORT` |
| Google Trends fails | `playwright install chromium`; network access |

---

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

---

**Built for catching hot stories before they blow up** 🔥
