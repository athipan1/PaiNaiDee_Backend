from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PostMediaCreate(BaseModel):
    """Schema for creating post media"""
    media_type: str = Field(..., pattern="^(image|video)$", description="Media type")
    url: str = Field(..., description="Media URL")
    thumb_url: Optional[str] = Field(None, description="Thumbnail URL")
    ordering: int = Field(default=0, description="Media ordering")


class PostCreate(BaseModel):
    """Schema for creating a post"""
    caption: Optional[str] = Field(None, max_length=2000, description="Post caption")
    tags: List[str] = Field(default=[], description="Post tags")
    location_id: Optional[str] = Field(None, description="Associated location ID")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    media: List[PostMediaCreate] = Field(..., min_items=1, description="Post media")


class PostResponse(BaseModel):
    """Schema for post response"""
    id: str = Field(..., description="Post ID")
    user_id: str = Field(..., description="User ID")
    caption: Optional[str] = Field(None, description="Post caption")
    tags: List[str] = Field(default=[], description="Post tags")
    location_id: Optional[str] = Field(None, description="Location ID")
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    like_count: int = Field(..., description="Number of likes")
    comment_count: int = Field(..., description="Number of comments")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PostUploadResponse(BaseModel):
    """Schema for post upload response"""
    success: bool = Field(..., description="Upload success status")
    post: PostResponse = Field(..., description="Created post")
    location_matched: Optional[str] = Field(None, description="Auto-matched location name")
    message: str = Field(..., description="Response message")


class PostListResponse(BaseModel):
    """Schema for listing posts response"""
    posts: List[PostResponse] = Field(..., description="List of posts")
    total_count: int = Field(..., description="Total number of posts")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of posts per page")
    total_pages: int = Field(..., description="Total number of pages")