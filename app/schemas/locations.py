from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LocationCreate(BaseModel):
    """Schema for creating a location"""
    name: str = Field(..., min_length=1, max_length=255, description="Location name")
    province: Optional[str] = Field(None, max_length=100, description="Province")
    aliases: List[str] = Field(default=[], description="Location aliases")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    popularity_score: int = Field(default=0, description="Popularity score")


class LocationResponse(BaseModel):
    """Schema for location response"""
    id: str = Field(..., description="Location ID")
    name: str = Field(..., description="Location name")
    province: Optional[str] = Field(None, description="Province")
    aliases: List[str] = Field(default=[], description="Location aliases")
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    popularity_score: int = Field(..., description="Popularity score")
    created_at: datetime = Field(..., description="Creation timestamp")
    distance_km: Optional[float] = Field(None, description="Distance from user location in kilometers")
    posts_count: Optional[int] = Field(None, description="Number of associated posts")


class LocationListResponse(BaseModel):
    """Schema for location list response"""
    locations: List[LocationResponse] = Field(..., description="List of locations")
    total_count: int = Field(..., description="Total number of locations")
    has_more: bool = Field(..., description="Whether more results are available")
    filters: dict = Field(default={}, description="Applied filters")


class LocationDetailResponse(LocationResponse):
    """Schema for detailed location response"""
    posts_count: int = Field(..., description="Number of associated posts")
    nearby_locations: List[LocationResponse] = Field(default=[], description="Nearby locations")


class NearbyLocationResponse(BaseModel):
    """Schema for nearby location response"""
    locations: List[LocationResponse] = Field(..., description="Nearby locations")
    radius_km: float = Field(..., description="Search radius used")
    total_count: int = Field(..., description="Total number of nearby locations")


class AutocompleteLocationResponse(BaseModel):
    """Schema for location autocomplete response"""
    suggestions: List[LocationResponse] = Field(..., description="Location suggestions")
    query: str = Field(..., description="Original query")
    total_count: int = Field(..., description="Total number of suggestions")