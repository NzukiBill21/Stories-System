-- Story Intelligence Dashboard - Database Schema
-- MySQL 5.7+ / MariaDB
-- Generated from backend/models.py

-- Create database
CREATE DATABASE IF NOT EXISTS story_intelligence
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE story_intelligence;

-- ---------------------------------------------------------------------------
-- Table: sources - Social media sources/accounts to monitor
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  platform VARCHAR(50) NOT NULL,
  account_handle VARCHAR(255) NOT NULL,
  account_name VARCHAR(255),
  account_id VARCHAR(255),
  is_active TINYINT(1) DEFAULT 1,
  is_trusted TINYINT(1) DEFAULT 0,
  is_kenyan TINYINT(1) DEFAULT 0,
  location VARCHAR(255),
  scrape_frequency_minutes INT DEFAULT 15,
  last_checked_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_source_platform_handle (platform, account_handle),
  INDEX idx_source_kenyan (is_kenyan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Table: hashtags - Hashtags to track for trending content
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hashtags (
  id INT AUTO_INCREMENT PRIMARY KEY,
  hashtag VARCHAR(255) NOT NULL UNIQUE,
  platform VARCHAR(50) DEFAULT 'all',
  is_kenyan TINYINT(1) DEFAULT 1,
  is_active TINYINT(1) DEFAULT 1,
  posts_per_hashtag INT DEFAULT 20,
  min_engagement INT DEFAULT 100,
  last_scraped_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_hashtag_platform (platform, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Table: raw_posts - Raw posts fetched from social media platforms
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source_id INT,
  hashtag_id INT,
  platform_post_id VARCHAR(255) NOT NULL,
  platform VARCHAR(50) NOT NULL,
  author VARCHAR(255) NOT NULL,
  content TEXT,
  url VARCHAR(500) NOT NULL,
  posted_at DATETIME NOT NULL,
  likes INT DEFAULT 0,
  comments INT DEFAULT 0,
  shares INT DEFAULT 0,
  views INT DEFAULT 0,
  location VARCHAR(255),
  is_kenyan TINYINT(1) DEFAULT 0,
  media_url VARCHAR(500),
  raw_data TEXT,
  fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL,
  FOREIGN KEY (hashtag_id) REFERENCES hashtags(id) ON DELETE SET NULL,
  INDEX idx_raw_post_platform_id (platform, platform_post_id),
  INDEX idx_raw_post_posted_at (posted_at),
  INDEX idx_raw_post_location (location),
  INDEX idx_raw_post_kenyan (is_kenyan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Table: stories - Scored, filtered stories ready for dashboard
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  raw_post_id INT NOT NULL UNIQUE,
  platform VARCHAR(50) NOT NULL,
  author VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  url VARCHAR(500) NOT NULL,
  posted_at DATETIME NOT NULL,
  likes INT DEFAULT 0,
  comments INT DEFAULT 0,
  shares INT DEFAULT 0,
  views INT DEFAULT 0,
  score FLOAT NOT NULL,
  engagement_velocity FLOAT,
  credibility_score FLOAT DEFAULT 0.0,
  topic_relevance_score FLOAT DEFAULT 0.0,
  location VARCHAR(255),
  is_kenyan TINYINT(1) DEFAULT 0,
  headline VARCHAR(500),
  reason_flagged VARCHAR(255),
  topic VARCHAR(255),
  is_active TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (raw_post_id) REFERENCES raw_posts(id) ON DELETE CASCADE,
  INDEX idx_story_score (score),
  INDEX idx_story_posted_at (posted_at),
  INDEX idx_story_active (is_active),
  INDEX idx_story_kenyan (is_kenyan),
  INDEX idx_story_location (location),
  INDEX idx_story_engagement_velocity (engagement_velocity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Table: scrape_logs - Log for scraping operations
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scrape_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source_id INT,
  hashtag_id INT,
  scrape_type VARCHAR(50) DEFAULT 'source',
  status VARCHAR(50) NOT NULL,
  posts_fetched INT DEFAULT 0,
  posts_processed INT DEFAULT 0,
  stories_created INT DEFAULT 0,
  error_message TEXT,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  duration_seconds FLOAT,
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL,
  FOREIGN KEY (hashtag_id) REFERENCES hashtags(id) ON DELETE SET NULL,
  INDEX idx_scrape_log_source (source_id),
  INDEX idx_scrape_log_hashtag (hashtag_id),
  INDEX idx_scrape_log_status (status),
  INDEX idx_scrape_log_started (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
