"""Platform scrapers module."""
from platforms.twitter import TwitterScraper
from platforms.facebook import FacebookScraper
from platforms.instagram import InstagramScraper
from platforms.tiktok import TikTokScraper


def get_scraper(platform: str):
    """Get the appropriate scraper for a platform."""
    scrapers = {
        'X': TwitterScraper,
        'Twitter': TwitterScraper,
        'Facebook': FacebookScraper,
        'Instagram': InstagramScraper,
        'TikTok': TikTokScraper,
    }
    
    scraper_class = scrapers.get(platform)
    if scraper_class:
        return scraper_class()
    else:
        raise ValueError(f"Unknown platform: {platform}")
