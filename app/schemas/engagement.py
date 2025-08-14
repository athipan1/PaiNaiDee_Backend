from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PostLikeCreate(BaseModel):
    """Schema for creating a post like"""
    post_id: str = Field(..., description="Post ID to like")


class PostLikeResponse(BaseModel):
    """Schema for post like response"""
    id: str = Field(..., description="Like ID")
    post_id: str = Field(..., description="Post ID")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")


class PostCommentCreate(BaseModel):
    """Schema for creating a post comment"""
    post_id: str = Field(..., description="Post ID to comment on")
    content: str = Field(..., min_length=1, max_length=500, description="Comment content")


class PostCommentUpdate(BaseModel):
    """Schema for updating a post comment"""
    content: str = Field(..., min_length=1, max_length=500, description="Updated comment content")


class PostCommentResponse(BaseModel):
    """Schema for post comment response"""
    id: str = Field(..., description="Comment ID")
    post_id: str = Field(..., description="Post ID")
    user_id: str = Field(..., description="User ID")
    content: str = Field(..., description="Comment content")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PostEngagementResponse(BaseModel):
    """Schema for post engagement summary"""
    post_id: str = Field(..., description="Post ID")
    like_count: int = Field(..., description="Number of likes")
    comment_count: int = Field(..., description="Number of comments")
    user_liked: bool = Field(..., description="Whether current user liked this post")
    recent_comments: List[PostCommentResponse] = Field(default=[], description="Recent comments")


class EngagementActionResponse(BaseModel):
    """Schema for engagement action responses"""
    success: bool = Field(..., description="Action success status")
    message: str = Field(..., description="Response message")
    like_count: Optional[int] = Field(None, description="Updated like count")
    comment_count: Optional[int] = Field(None, description="Updated comment count")