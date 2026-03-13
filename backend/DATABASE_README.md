# Database Structure — Story Intelligence Dashboard

This document describes the database schema for the Story Intelligence Dashboard. The database stores social media sources, scraped posts, scored stories, and scraping logs.

---

## Overview

- **Database:** `story_intelligence`
- **Engine:** MySQL 5.7+ / MariaDB
- **Charset:** `utf8mb4`
- **Tables:** 5 (sources, hashtags, raw_posts, stories, scrape_logs)

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐
│   sources   │       │   hashtags  │
└──────┬──────┘       └──────┬──────┘
       │                     │
       │ source_id           │ hashtag_id
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
           ┌─────────────┐
           │  raw_posts  │
           └──────┬──────┘
                  │
                  │ raw_post_id (1:1)
                  │
                  ▼
           ┌─────────────┐       ┌─────────────┐
           │   stories   │       │ scrape_logs │
           └─────────────┘       └──────▲──────┘
                                        │
                        source_id ──────┼────── hashtag_id
```

---

## Tables

### 1. `sources`

Accounts or feeds to monitor (X, Facebook, Instagram, TikTok, RSS, etc.).

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `platform` | VARCHAR(50) | Platform name (X, Facebook, Instagram, TikTok, RSS, GoogleTrends, YouTube, Reddit) |
| `account_handle` | VARCHAR(255) | @username or page identifier |
| `account_name` | VARCHAR(255) | Display name |
| `account_id` | VARCHAR(255) | Platform-specific ID (optional) |
| `is_active` | TINYINT(1) | Whether scraping is enabled (default: 1) |
| `is_trusted` | TINYINT(1) | High-credibility source (default: 0) |
| `is_kenyan` | TINYINT(1) | Kenyan content flag (default: 0) |
| `location` | VARCHAR(255) | Location filter (e.g. Nairobi, Kenya) |
| `scrape_frequency_minutes` | INT | Scrape interval in minutes (default: 15) |
| `last_checked_at` | DATETIME | Last scrape time |
| `created_at` | DATETIME | Creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |

**Indexes:** `(platform, account_handle)`, `is_kenyan`

**Relationships:** One source → many `raw_posts`; one source → many `scrape_logs`

---

### 2. `hashtags`

Hashtags used to discover trending content.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `hashtag` | VARCHAR(255) UNIQUE | Hashtag text (e.g. #KenyaElections) |
| `platform` | VARCHAR(50) | Target platform or "all" (default: all) |
| `is_kenyan` | TINYINT(1) | Kenyan-related flag (default: 1) |
| `is_active` | TINYINT(1) | Whether to scrape (default: 1) |
| `posts_per_hashtag` | INT | Max posts per scrape (default: 20) |
| `min_engagement` | INT | Minimum engagement to include (default: 100) |
| `last_scraped_at` | DATETIME | Last scrape time |
| `created_at` | DATETIME | Creation timestamp |

**Indexes:** `(platform, is_active)`

**Relationships:** One hashtag → many `raw_posts`; one hashtag → many `scrape_logs`

---

### 3. `raw_posts`

Raw posts from scrapers before scoring.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `source_id` | INT (FK) | Source (nullable for hashtag-only posts) |
| `hashtag_id` | INT (FK) | Hashtag (nullable for source-only posts) |
| `platform_post_id` | VARCHAR(255) | Platform post ID |
| `platform` | VARCHAR(50) | Platform name |
| `author` | VARCHAR(255) | Post author |
| `content` | TEXT | Post text |
| `url` | VARCHAR(500) | Post URL |
| `posted_at` | DATETIME | Original post time |
| `likes` | INT | Likes (default: 0) |
| `comments` | INT | Comments (default: 0) |
| `shares` | INT | Shares / retweets (default: 0) |
| `views` | INT | Views (default: 0) |
| `location` | VARCHAR(255) | Extracted location |
| `is_kenyan` | TINYINT(1) | Kenyan content flag (default: 0) |
| `media_url` | VARCHAR(500) | Image or video URL |
| `raw_data` | TEXT | Raw JSON response |
| `fetched_at` | DATETIME | When post was fetched |

**Indexes:** `(platform, platform_post_id)`, `posted_at`, `location`, `is_kenyan`

**Relationships:** Belongs to `sources` and/or `hashtags`; has one `story` per raw post

---

### 4. `stories`

Scored, filtered stories used by the dashboard.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `raw_post_id` | INT (FK, UNIQUE) | Link to `raw_posts` (one-to-one) |
| `platform` | VARCHAR(50) | Platform name |
| `author` | VARCHAR(255) | Author |
| `content` | TEXT | Post content |
| `url` | VARCHAR(500) | Post URL |
| `posted_at` | DATETIME | Original post time |
| `likes` | INT | Likes |
| `comments` | INT | Comments |
| `shares` | INT | Shares |
| `views` | INT | Views |
| `score` | FLOAT | Overall score (0–100) |
| `engagement_velocity` | FLOAT | Engagement per hour |
| `credibility_score` | FLOAT | Source credibility (default: 0.0) |
| `topic_relevance_score` | FLOAT | Topic relevance (default: 0.0) |
| `location` | VARCHAR(255) | Location |
| `is_kenyan` | TINYINT(1) | Kenyan content flag (default: 0) |
| `headline` | VARCHAR(500) | Headline for display |
| `reason_flagged` | VARCHAR(255) | Reason for flagging |
| `topic` | VARCHAR(255) | Category (politics, entertainment, etc.) |
| `is_active` | TINYINT(1) | Still trending (default: 1) |
| `created_at` | DATETIME | Creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |

**Indexes:** `score`, `posted_at`, `is_active`, `is_kenyan`, `location`, `engagement_velocity`

**Relationships:** One story per `raw_post` (via `raw_post_id`)

---

### 5. `scrape_logs`

Logs for each scraping run.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `source_id` | INT (FK) | Source (nullable for hashtag scrapes) |
| `hashtag_id` | INT (FK) | Hashtag (nullable for source scrapes) |
| `scrape_type` | VARCHAR(50) | `source`, `hashtag`, or `location` (default: source) |
| `status` | VARCHAR(50) | `success`, `error`, `rate_limited` |
| `posts_fetched` | INT | Posts fetched (default: 0) |
| `posts_processed` | INT | Posts processed (default: 0) |
| `stories_created` | INT | Stories created (default: 0) |
| `error_message` | TEXT | Error details if failed |
| `started_at` | DATETIME | Start time |
| `completed_at` | DATETIME | End time |
| `duration_seconds` | FLOAT | Duration in seconds |

**Indexes:** `source_id`, `hashtag_id`, `status`, `started_at`

**Relationships:** Linked to `sources` and/or `hashtags`

---

## Data Flow

1. **Sources & hashtags** define what to scrape (`sources`, `hashtags`).
2. **Scrapers** fetch posts and store them as **raw_posts**.
3. **Scoring** turns qualifying raw posts into **stories**.
4. **Dashboard** reads from **stories** and related fields.
5. **Logs** record each scrape run in **scrape_logs**.

```
sources/hashtags → raw_posts → (scoring) → stories → dashboard
                         ↓
                  scrape_logs
```

---

## Applying the Schema

**Option 1 — SQL file:**
```bash
mysql -u root -p < backend/schema.sql
```

**Option 2 — Python (also seeds sample sources):**
```bash
cd backend
python init_db.py
```

---

## Related Files

| File | Purpose |
|------|---------|
| `backend/models.py` | SQLAlchemy ORM definitions |
| `backend/schema.sql` | DDL script |
| `backend/database.py` | Connection and session setup |
