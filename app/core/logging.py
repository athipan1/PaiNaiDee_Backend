import logging
import json
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager


class StructuredLogger:
    """Structured logging for analytics events"""
    
    def __init__(self, name: str = "painaidee_api"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatter for structured JSON logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log a structured event"""
        log_data = {
            "event_type": event_type,
            "timestamp": time.time(),
            **data
        }
        self.logger.info(json.dumps(log_data))
    
    def search_performed(self, query: str, normalized: str, result_count: int, latency_ms: float) -> None:
        """Log search.performed event"""
        self.log_event("search.performed", {
            "query": query,
            "normalized": normalized,
            "resultCount": result_count,
            "latencyMs": latency_ms
        })
    
    def post_uploaded(self, post_id: str, has_geo: bool, location_matched: Optional[str] = None) -> None:
        """Log post.upload event"""
        self.log_event("post.upload", {
            "postId": post_id,
            "hasGeo": has_geo,
            "locationMatched": location_matched
        })
    
    def location_nearby_request(self, location_id: str, radius_km: float, result_count: int) -> None:
        """Log location.nearby.request event"""
        self.log_event("location.nearby.request", {
            "locationId": location_id,
            "radiusKm": radius_km,
            "resultCount": result_count
        })


# Global logger instance
logger = StructuredLogger()


@contextmanager
def log_time(event_type: str, extra_data: Optional[Dict[str, Any]] = None):
    """Context manager to time operations and log results"""
    start_time = time.time()
    extra_data = extra_data or {}
    
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_event(event_type, {
            **extra_data,
            "durationMs": duration_ms
        })