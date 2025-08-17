import math
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional
from app.core.config import settings


def calculate_popularity_score(like_count: int, comment_count: int) -> float:
    """
    Calculate normalized popularity score

    Args:
        like_count: Number of likes
        comment_count: Number of comments

    Returns:
        Normalized popularity score (0-1)
    """
    alpha_comment = settings.alpha_comment
    raw_score = like_count + (alpha_comment * comment_count)

    # Improved normalization using sigmoid-like function
    # This ensures the score stays within 0-1 range
    max_expected_score = 1000  # Adjust based on typical content engagement
    normalized_score = raw_score / (raw_score + max_expected_score)

    return min(normalized_score, 1.0)  # Ensure it never exceeds 1.0


def calculate_recency_decay(created_at: datetime) -> float:
    """
    Calculate recency decay score

    Args:
        created_at: When the content was created

    Returns:
        Recency decay score (0-1)
    """
    now = datetime.now(timezone.utc)
    age_minutes = (now - created_at).total_seconds() / 60
    tau_minutes = settings.tau_minutes

    # Exponential decay
    return math.exp(-age_minutes / tau_minutes)


def calculate_combined_score(
    like_count: int,
    comment_count: int,
    created_at: datetime,
    weights: Optional[Dict[str, float]] = None
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate combined ranking score

    Args:
        like_count: Number of likes
        comment_count: Number of comments
        created_at: When content was created
        weights: Custom weights (optional)

    Returns:
        Tuple of (combined_score, component_scores)
    """
    if weights is None:
        weights = settings.search_weights

    w_pop = weights.get("w_pop", 0.7)
    w_recency = weights.get("w_recency", 0.3)

    popularity_norm = calculate_popularity_score(like_count, comment_count)
    recency_decay = calculate_recency_decay(created_at)

    combined_score = (w_pop * popularity_norm) + (w_recency * recency_decay)

    component_scores: Dict[str, float] = {
        "popularity": popularity_norm,
        "recency": recency_decay,
        "combined": combined_score,
    }

    return combined_score, component_scores


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate haversine distance between two points in kilometers

    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Earth radius in kilometers
    earth_radius = 6371

    return earth_radius * c
