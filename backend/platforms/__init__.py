"""Platform scrapers module."""
from platforms.twitter import TwitterScraper
from platforms.facebook import FacebookScraper
from platforms.instagram import InstagramScraper
from platforms.tiktok import TikTokScraper
from platforms.rss import RSSScraper
from platforms.reddit import RedditScraper
from platforms.google_trends import GoogleTrendsScraper


def get_scraper(platform: str):
    """Get the appropriate scraper for a platform."""
    scrapers = {
        'X': TwitterScraper,
        'Twitter': TwitterScraper,
        'Facebook': FacebookScraper,
        'Instagram': InstagramScraper,
        'TikTok': TikTokScraper,
        'RSS': RSSScraper,
        'Reddit': RedditScraper,
        'GoogleTrends': GoogleTrendsScraper,
    }
    
    scraper_class = scrapers.get(platform)
    if scraper_class:
        return scraper_class()
    else:
        raise ValueError(f"Unknown platform: {platform}")
