"""Configuration for Kenyan sources, hashtags, and locations."""
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class SourceConfig:
    """Configuration for a social media source."""
    platform: str
    account_handle: str
    account_name: str
    account_id: str = None
    is_trusted: bool = False
    is_kenyan: bool = False
    location: str = None  # e.g., "Nairobi", "Kenya"
    scrape_frequency_minutes: int = 15


@dataclass
class HashtagConfig:
    """Configuration for hashtag tracking."""
    hashtag: str
    platform: str  # "all", "X", "Instagram", "Facebook", "TikTok"
    is_kenyan: bool = True
    posts_per_hashtag: int = 20
    min_engagement: int = 100  # Minimum likes/views to consider


# Global sources
GLOBAL_SOURCES = [
    SourceConfig(
        platform="X",
        account_handle="@BBCNews",
        account_name="BBC News",
        is_trusted=True,
        is_kenyan=False,
        scrape_frequency_minutes=15
    ),
    SourceConfig(
        platform="X",
        account_handle="@CNN",
        account_name="CNN",
        is_trusted=True,
        is_kenyan=False,
        scrape_frequency_minutes=15
    ),
    SourceConfig(
        platform="X",
        account_handle="@Reuters",
        account_name="Reuters",
        is_trusted=True,
        is_kenyan=False,
        scrape_frequency_minutes=15
    ),
]

# Kenyan media sources
KENYAN_SOURCES = [
    # Kenyan News Media
    SourceConfig(
        platform="X",
        account_handle="@NationAfrica",
        account_name="Nation Africa",
        is_trusted=True,
        is_kenyan=True,
        location="Kenya",
        scrape_frequency_minutes=15
    ),
    SourceConfig(
        platform="X",
        account_handle="@StandardKenya",
        account_name="Standard Digital",
        is_trusted=True,
        is_kenyan=True,
        location="Kenya",
        scrape_frequency_minutes=15
    ),
    SourceConfig(
        platform="X",
        account_handle="@TukoNews",
        account_name="Tuko News",
        is_trusted=True,
        is_kenyan=True,
        location="Kenya",
        scrape_frequency_minutes=15
    ),
    SourceConfig(
        platform="Facebook",
        account_handle="NationAfrica",
        account_name="Nation Africa",
        is_trusted=True,
        is_kenyan=True,
        location="Kenya",
        scrape_frequency_minutes=30
    ),
    SourceConfig(
        platform="Instagram",
        account_handle="nationafrica",
        account_name="Nation Africa",
        is_trusted=True,
        is_kenyan=True,
        location="Kenya",
        scrape_frequency_minutes=30
    ),
]

# Kenyan hashtags to track
KENYAN_HASHTAGS = [
    HashtagConfig(hashtag="#KenyaElections", platform="all", is_kenyan=True, posts_per_hashtag=30),
    HashtagConfig(hashtag="#Nairobi", platform="all", is_kenyan=True, posts_per_hashtag=20),
    HashtagConfig(hashtag="#Mombasa", platform="all", is_kenyan=True, posts_per_hashtag=20),
    HashtagConfig(hashtag="#TrendingKenya", platform="all", is_kenyan=True, posts_per_hashtag=25),
    HashtagConfig(hashtag="#Kenya", platform="all", is_kenyan=True, posts_per_hashtag=30),
    HashtagConfig(hashtag="#KenyaNews", platform="all", is_kenyan=True, posts_per_hashtag=20),
    HashtagConfig(hashtag="#KenyaPolitics", platform="X", is_kenyan=True, posts_per_hashtag=15),
    HashtagConfig(hashtag="#NairobiTrending", platform="all", is_kenyan=True, posts_per_hashtag=15),
]

# Popular topics/keywords for Kenya
KENYAN_KEYWORDS = [
    "Kenya elections",
    "Nairobi news",
    "Mombasa",
    "Kenyan politics",
    "Kenya entertainment",
    "Kenya sports",
    "Kenya tech",
    "Ruto",
    "Raila",
    "Kenya breaking",
    "Kenya trending",
]

# Kenyan locations for geotag filtering
KENYAN_LOCATIONS = [
    "Nairobi",
    "Mombasa",
    "Kisumu",
    "Nakuru",
    "Eldoret",
    "Kenya",
    "Nairobi, Kenya",
    "Mombasa, Kenya",
]


def get_all_sources() -> List[SourceConfig]:
    """Get all configured sources (global + Kenyan)."""
    return GLOBAL_SOURCES + KENYAN_SOURCES


def get_kenyan_sources() -> List[SourceConfig]:
    """Get only Kenyan sources."""
    return [s for s in get_all_sources() if s.is_kenyan]


def get_hashtags_for_platform(platform: str) -> List[HashtagConfig]:
    """Get hashtags for a specific platform."""
    return [h for h in KENYAN_HASHTAGS if h.platform == "all" or h.platform == platform]


def get_all_hashtags() -> List[str]:
    """Get all hashtag strings."""
    return [h.hashtag for h in KENYAN_HASHTAGS]
