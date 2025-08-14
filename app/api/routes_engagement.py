from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_async_db
from app.services.engagement_service import engagement_service
from app.schemas.engagement import (
    PostLikeCreate, PostLikeResponse,
    PostCommentCreate, PostCommentUpdate, PostCommentResponse,
    PostEngagementResponse, EngagementActionResponse
)

router = APIRouter(prefix="/api", tags=["engagement"])


def get_current_user_id() -> str:
    """
    TODO: Extract user ID from JWT token
    For now, return a dummy user ID for Phase 1 testing
    """
    return "user_123_demo"  # TODO: Replace with actual auth


@router.post("/posts/{post_id}/like", response_model=EngagementActionResponse)
async def like_post(
    post_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Like or unlike a post.
    
    **Toggle behavior:**
    - If user hasn't liked the post, it will be liked
    - If user already liked the post, it will be unliked
    
    **Returns:**
    - Success status and updated like count
    - Error message if post not found or invalid ID
    
    **Authentication required.**
    """
    try:
        result = await engagement_service.like_post(post_id, current_user_id, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process like action: {str(e)}"
        )


@router.post("/posts/{post_id}/comments", response_model=PostCommentResponse)
async def create_comment(
    post_id: str,
    comment_data: PostCommentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Add a comment to a post.
    
    **Request body:**
    - `content`: Comment text (1-500 characters)
    
    **Returns:**
    - Created comment details
    
    **Authentication required.**
    """
    try:
        # Ensure post_id matches the URL parameter
        comment_data.post_id = post_id
        
        result = await engagement_service.comment_on_post(comment_data, current_user_id, db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}"
        )


@router.put("/comments/{comment_id}", response_model=PostCommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: PostCommentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update a comment (only by the comment author).
    
    **Request body:**
    - `content`: Updated comment text (1-500 characters)
    
    **Returns:**
    - Updated comment details
    
    **Authorization:**
    - Only the comment author can update their comment
    
    **Authentication required.**
    """
    try:
        result = await engagement_service.update_comment(comment_id, comment_data, current_user_id, db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}"
        )


@router.delete("/comments/{comment_id}", response_model=EngagementActionResponse)
async def delete_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a comment (only by the comment author).
    
    **Returns:**
    - Success status and updated comment count
    
    **Authorization:**
    - Only the comment author can delete their comment
    
    **Authentication required.**
    """
    try:
        result = await engagement_service.delete_comment(comment_id, current_user_id, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}"
        )


@router.get("/posts/{post_id}/engagement", response_model=PostEngagementResponse)
async def get_post_engagement(
    post_id: str,
    limit_comments: Optional[int] = 5,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get engagement data for a post.
    
    **Returns:**
    - Like count and comment count
    - Whether current user liked the post
    - Recent comments (default: 5 most recent)
    
    **Query parameters:**
    - `limit_comments`: Number of recent comments to include (default: 5, max: 20)
    
    **Authentication required.**
    """
    if limit_comments and limit_comments > 20:
        limit_comments = 20
    
    try:
        result = await engagement_service.get_post_engagement(
            post_id, current_user_id, db, limit_comments or 5
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get post engagement: {str(e)}"
        )