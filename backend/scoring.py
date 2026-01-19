"""Scoring system for posts based on engagement, credibility, and trending."""
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import settings
from kenyan_sources_config import KENYAN_KEYWORDS, KENYAN_LOCATIONS


def calculate_engagement_velocity(
    likes: int,
    comments: int,
    shares: int,
    views: int,
    posted_at: datetime,
    current_time: Optional[datetime] = None
) -> float:
    """
    Calculate engagement velocity (engagement per hour).
    
    Args:
        likes: Number of likes
        comments: Number of comments
        shares: Number of shares/retweets
        views: Number of views
        posted_at: When the post was created
        current_time: Current time (defaults to now)
    
    Returns:
        Engagement velocity (total engagement per hour)
    """
    if current_time is None:
        current_time = datetime.now(posted_at.tzinfo) if posted_at.tzinfo else datetime.utcnow()
    
    # Calculate hours since posting
    time_diff = current_time - posted_at
    hours_elapsed = max(time_diff.total_seconds() / 3600, 0.1)  # At least 0.1 hours
    
    # Weighted engagement metric
    # Views are less valuable, so we weight them lower
    total_engagement = likes + (comments * 2) + (shares * 3) + (views * 0.1)
    
    # Engagement per hour
    velocity = total_engagement / hours_elapsed
    
    return velocity


def calculate_credibility_score(
    account_handle: str,
    is_trusted_source: bool = False
) -> float:
    """
    Calculate credibility score based on source trust.
    
    Args:
        account_handle: The account handle/username
        is_trusted_source: Whether this is a predefined trusted source
    
    Returns:
        Credibility score (0-100)
    """
    if is_trusted_source:
        return 100.0
    
    # Check if handle is in trusted sources list
    handle_lower = account_handle.lower().strip()
    trusted_handles = [s.lower().strip() for s in settings.trusted_sources]
    
    if handle_lower in trusted_handles:
        return 100.0
    
    # Default credibility for unknown sources
    # Could be enhanced with verification badges, follower count, etc.
    return 50.0


def calculate_topic_relevance_score(content: str, is_kenyan: bool = False, location: str = None) -> float:
    """
    Calculate topic relevance score based on trending keywords.
    Prioritizes Kenyan content and keywords.
    
    Args:
        content: Post content text
        is_kenyan: Whether this is Kenyan content
        location: Location string if available
    
    Returns:
        Topic relevance score (0-100)
    """
    if not content:
        return 0.0
    
    content_lower = content.lower()
    
    # Combine configured keywords with Kenyan keywords
    all_keywords = [kw.lower() for kw in settings.trending_keywords] + [kw.lower() for kw in KENYAN_KEYWORDS]
    
    if not all_keywords:
        return 50.0  # Default if no keywords configured
    
    # Count keyword matches
    matches = sum(1 for keyword in all_keywords if keyword in content_lower)
    
    # Boost score for Kenyan content (increased priority)
    kenyan_boost = 30.0 if is_kenyan else 0.0
    
    # Boost score for Kenyan locations (increased priority)
    location_boost = 0.0
    if location:
        location_lower = location.lower()
        # Check for Kenyan locations
        if any(kenyan_loc.lower() in location_lower for kenyan_loc in KENYAN_LOCATIONS):
            location_boost = 25.0
        # Check for other African locations
        elif any(african_loc in location_lower for african_loc in ['africa', 'nairobi', 'mombasa', 'lagos', 'johannesburg', 'cairo', 'accra', 'dar es salaam', 'kampala']):
            location_boost = 15.0
    
    # Score based on number of matches
    # More matches = higher relevance
    # Boost for trending keywords (breaking, viral, trending, etc.)
    trending_keywords_boost = 0.0
    trending_indicators = ['breaking', 'viral', 'trending', 'shocking', 'exclusive', 
                          'outrage', 'controversy', 'emergency', 'scandal']
    if any(indicator in content_lower for indicator in trending_indicators):
        trending_keywords_boost = 25.0
    
    base_score = min(matches * 20, 100)  # 20 points per keyword, max 100
    total_score = min(base_score + kenyan_boost + location_boost + trending_keywords_boost, 100)
    
    return total_score


def calculate_overall_score(
    engagement_velocity: float,
    credibility_score: float,
    topic_relevance_score: float,
    likes: int,
    comments: int,
    shares: int,
    views: int,
    is_kenyan: bool = False,
    location: str = None
) -> tuple[float, str]:
    """
    Calculate overall score and reason for flagging.
    
    Args:
        engagement_velocity: Engagement velocity score
        credibility_score: Credibility score (0-100)
        topic_relevance_score: Topic relevance score (0-100)
        likes: Number of likes
        comments: Number of comments
        shares: Number of shares
        views: Number of views
    
    Returns:
        Tuple of (overall_score, reason_flagged)
    """
    # Weighted scoring
    # Engagement velocity: 50% weight
    # Credibility: 30% weight
    # Topic relevance: 20% weight
    
    # Normalize engagement velocity (assume max reasonable velocity is 1000/hour)
    normalized_velocity = min(engagement_velocity / 10.0, 100.0)  # Scale to 0-100
    
    overall_score = (
        normalized_velocity * 0.5 +
        credibility_score * 0.3 +
        topic_relevance_score * 0.2
    )
    
    # Determine reason for flagging
    reasons = []
    
    if engagement_velocity >= settings.min_engagement_velocity * 2:
        reasons.append("High engagement velocity")
    elif engagement_velocity >= settings.min_engagement_velocity:
        reasons.append("Rising engagement")
    
    if credibility_score >= 80:
        reasons.append("Trusted source")
    
    if topic_relevance_score >= 60:
        reasons.append("Trending topic")
    
    if is_kenyan:
        reasons.append("Kenyan content")
        # Boost overall score for Kenyan content
        overall_score += 15.0
    
    if location:
        location_lower = location.lower()
        if any(kenyan_loc.lower() in location_lower for kenyan_loc in KENYAN_LOCATIONS):
            reasons.append("Kenyan location")
            overall_score += 10.0
        elif any(african_loc in location_lower for african_loc in ['africa', 'nairobi', 'mombasa', 'lagos', 'johannesburg', 'cairo', 'accra']):
            reasons.append("African location")
            overall_score += 5.0
    
    if likes >= 1000 or comments >= 100 or shares >= 50:
        reasons.append("High engagement metrics")
    
    reason_flagged = ", ".join(reasons) if reasons else "Moderate engagement"
    
    return overall_score, reason_flagged


def should_keep_post(score: float, engagement_velocity: float) -> bool:
    """
    Determine if a post should be kept based on thresholds.
    
    Args:
        score: Overall score
        engagement_velocity: Engagement velocity
    
    Returns:
        True if post should be kept, False otherwise
    """
    return (
        score >= settings.min_engagement_score and
        engagement_velocity >= settings.min_engagement_velocity
    )
