import pytest
from datetime import datetime, timezone, timedelta
from app.utils.ranking import (
    calculate_popularity_score,
    calculate_recency_decay,
    calculate_combined_score,
    haversine_distance
)


class TestRanking:
    """Test ranking utilities"""
    
    def test_calculate_popularity_score(self):
        """Test popularity score calculation"""
        # Basic scores
        assert calculate_popularity_score(0, 0) >= 0
        assert calculate_popularity_score(10, 5) > calculate_popularity_score(5, 2)
        assert calculate_popularity_score(100, 0) > calculate_popularity_score(50, 0)
        
        # Comments weighted higher than likes
        score_likes = calculate_popularity_score(10, 0)
        score_comments = calculate_popularity_score(0, 5)  # 5 comments = 10 likes with alpha=2
        assert score_comments >= score_likes
        
        # Normalization (should be 0-1 range)
        score = calculate_popularity_score(1000, 500)
        assert 0 <= score <= 1
    
    def test_calculate_recency_decay(self):
        """Test recency decay calculation"""
        now = datetime.now(timezone.utc)
        
        # Recent content should have higher score
        recent = calculate_recency_decay(now - timedelta(minutes=60))
        old = calculate_recency_decay(now - timedelta(days=30))
        assert recent > old
        
        # Very recent content
        very_recent = calculate_recency_decay(now - timedelta(minutes=1))
        assert very_recent > recent
        
        # Score should be 0-1 range
        score = calculate_recency_decay(now - timedelta(days=1))
        assert 0 <= score <= 1
    
    def test_calculate_combined_score(self):
        """Test combined scoring"""
        now = datetime.now(timezone.utc)
        
        # Basic scoring
        score, components = calculate_combined_score(
            like_count=100,
            comment_count=20,
            created_at=now - timedelta(hours=1)
        )
        
        assert 0 <= score <= 1
        assert "popularity" in components
        assert "recency" in components
        assert "combined" in components
        
        # Custom weights
        custom_weights = {"w_pop": 0.8, "w_recency": 0.2}
        score_custom, _ = calculate_combined_score(
            like_count=100,
            comment_count=20,
            created_at=now - timedelta(hours=1),
            weights=custom_weights
        )
        
        assert 0 <= score_custom <= 1
        
        # Popular recent content should score higher than old content
        recent_score, _ = calculate_combined_score(50, 10, now - timedelta(hours=1))
        old_score, _ = calculate_combined_score(50, 10, now - timedelta(days=30))
        assert recent_score > old_score
    
    def test_haversine_distance(self):
        """Test geographic distance calculation"""
        # Same point
        assert haversine_distance(0, 0, 0, 0) == 0
        
        # Known distances (approximate)
        # Bangkok to Chiang Mai (roughly 600km)
        bkk_lat, bkk_lng = 13.7563, 100.5018
        cm_lat, cm_lng = 18.7883, 98.9853
        distance = haversine_distance(bkk_lat, bkk_lng, cm_lat, cm_lng)
        assert 500 < distance < 700  # Approximate distance
        
        # Short distance
        lat1, lng1 = 13.7563, 100.5018
        lat2, lng2 = 13.7573, 100.5028  # Very close points
        short_distance = haversine_distance(lat1, lng1, lat2, lng2)
        assert 0 < short_distance < 2  # Should be less than 2km
        
        # Distance should be symmetric
        d1 = haversine_distance(lat1, lng1, lat2, lng2)
        d2 = haversine_distance(lat2, lng2, lat1, lng1)
        assert abs(d1 - d2) < 0.001  # Should be essentially equal