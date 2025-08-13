from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SearchRequest(BaseModel):
    """Search request schema"""
    q: str = Field(..., min_length=1, max_length=500, description="Search query")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class MediaResponse(BaseModel):
    """Media response schema"""
    type: str = Field(..., description="Media type (image/video)")
    url: str = Field(..., description="Media URL")
    thumb_url: Optional[str] = Field(None, description="Thumbnail URL")


class LocationResponse(BaseModel):
    """Location response schema"""
    id: str = Field(..., description="Location ID")
    name: str = Field(..., description="Location name")
    province: Optional[str] = Field(None, description="Province")
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")


class PostResponse(BaseModel):
    """Post response schema"""
    id: str = Field(..., description="Post ID")
    caption: Optional[str] = Field(None, description="Post caption")
    media: List[MediaResponse] = Field(default=[], description="Post media")
    location: Optional[LocationResponse] = Field(None, description="Associated location")
    like_count: int = Field(..., description="Number of likes")
    comment_count: int = Field(..., description="Number of comments")
    created_at: datetime = Field(..., description="Creation timestamp")
    score: float = Field(..., description="Relevance score")


class SuggestionResponse(BaseModel):
    """Search suggestion schema"""
    type: str = Field(..., description="Suggestion type (place/tag/category)")
    text: str = Field(..., description="Suggestion text")


class SearchResponse(BaseModel):
    """Search response schema"""
    query: str = Field(..., description="Original search query")
    expansion: List[str] = Field(default=[], description="Expanded search terms")
    posts: List[PostResponse] = Field(default=[], description="Search results")
    suggestions: List[SuggestionResponse] = Field(default=[], description="Search suggestions")
    latency_ms: float = Field(..., description="Search latency in milliseconds")
    total_count: Optional[int] = Field(None, description="Total number of results")


class NearbyRequest(BaseModel):
    """Nearby places request schema"""
    radius_km: float = Field(default=10.0, ge=0.1, le=100.0, description="Search radius in kilometers")


class AutocompleteResponse(BaseModel):
    """Autocomplete response schema"""
    suggestions: List[str] = Field(..., description="Autocomplete suggestions")


class LocationDetailResponse(BaseModel):
    """Location detail response schema"""
    id: str = Field(..., description="Location ID")
    name: str = Field(..., description="Location name")
    province: Optional[str] = Field(None, description="Province")
    aliases: List[str] = Field(default=[], description="Location aliases")
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    popularity_score: int = Field(..., description="Popularity score")
    created_at: datetime = Field(..., description="Creation timestamp")
    posts_count: int = Field(..., description="Number of associated posts")