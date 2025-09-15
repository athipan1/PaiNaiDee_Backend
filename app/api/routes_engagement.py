from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_async_db
from app.services.engagement_service import engagement_service
from app.schemas.engagement import (
    PostLikeCreate, PostCommentCreate, PostCommentUpdate, PostCommentCreateRequest,
    PostCommentResponse, PostEngagementResponse, EngagementActionResponse, PostCommentsResponse
)
from app.auth.security import get_current_user, get_optional_current_user, verify_api_key
from src.models import User
from app.core.exceptions import NotFoundException, InvalidInputException, PermissionDeniedException

router = APIRouter(prefix="/api", tags=["engagement"])


@router.post("/posts/{post_id}/like", response_model=EngagementActionResponse)
async def like_post(
    post_id: str,
    db: AsyncSession = Depends(get_async_db),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_actor_id: Optional[str] = Header(None, alias="X-Actor-Id"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Like or unlike a post.
    
    **Authentication:**
    - Requires either valid JWT token or API key in X-API-Key header
    - If using API key, provide X-Actor-Id header for user identification
    
    **Path Parameters:**
    - `post_id`: UUID of the post to like/unlike
    
    **Features:**
    - If post is not liked, it will be liked
    - If post is already liked, it will be unliked (toggle behavior)
    - Updates the post's like count automatically
    - Returns the updated like count
    """
    # Get actor ID from user or header
    if current_user:
        actor_id = str(current_user.id)
    elif x_api_key and verify_api_key(x_api_key):
        if not x_actor_id:
            raise InvalidInputException(message="X-Actor-Id header required when using API key")
        actor_id = x_actor_id
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = await engagement_service.like_post(post_id, actor_id, db)
    if not result.success:
        if "not found" in result.message:
            raise NotFoundException(message=result.message)
        else:
            raise InvalidInputException(message=result.message)
    return result


@router.get("/posts/{post_id}/comments", response_model=PostCommentsResponse)
async def get_post_comments(
    post_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Comments per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get comments for a post with pagination.
    
    **Path Parameters:**
    - `post_id`: UUID of the post
    
    **Query Parameters:**
    - `page`: Page number (starting from 1)
    - `page_size`: Number of comments per page (1-50)
    
    **Features:**
    - Returns paginated list of comments
    - Comments are ordered by creation date (newest first)
    - Includes pagination metadata
    """
    result = await engagement_service.get_post_comments(post_id, page, page_size, db)
    if not result:
        raise NotFoundException(message="Post not found")
    return result


@router.post("/posts/{post_id}/comments", response_model=PostCommentResponse)
async def create_comment(
    post_id: str,
    comment_request: PostCommentCreateRequest,
    db: AsyncSession = Depends(get_async_db),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_actor_id: Optional[str] = Header(None, alias="X-Actor-Id"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Add a comment to a post.
    
    **Authentication:**
    - Requires either valid JWT token or API key in X-API-Key header
    - If using API key, provide X-Actor-Id header for user identification
    
    **Path Parameters:**
    - `post_id`: UUID of the post to comment on
    
    **Request Body:**
    - `content`: Comment text (1-500 characters)
    
    **Features:**
    - Automatically updates the post's comment count
    - Returns the created comment with timestamp
    """
    # Get actor ID from user or header
    if current_user:
        actor_id = str(current_user.id)
    elif x_api_key and verify_api_key(x_api_key):
        if not x_actor_id:
            raise InvalidInputException(message="X-Actor-Id header required when using API key")
        actor_id = x_actor_id
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create the full comment data with post_id from URL
    comment_data = PostCommentCreate(post_id=post_id, content=comment_request.content)
    result = await engagement_service.comment_on_post(comment_data, actor_id, db)
    return result


@router.put("/comments/{comment_id}", response_model=PostCommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: PostCommentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment (only by the comment author).
    
    **Path Parameters:**
    - `comment_id`: UUID of the comment to update
    
    **Request Body:**
    - `content`: Updated comment text (1-500 characters)
    
    **Features:**
    - Only the comment author can update their comment
    - Returns the updated comment with new timestamp
    """
    result = await engagement_service.update_comment(comment_id, comment_data, str(current_user.id), db)
    return result


@router.delete("/comments/{comment_id}", response_model=EngagementActionResponse)
async def delete_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment (only by the comment author).
    
    **Path Parameters:**
    - `comment_id`: UUID of the comment to delete
    
    **Features:**
    - Only the comment author can delete their comment
    - Automatically updates the post's comment count
    - Returns the updated comment count
    """
    result = await engagement_service.delete_comment(comment_id, str(current_user.id), db)
    if not result.success:
        if "not found" in result.message:
            raise NotFoundException(message=result.message)
        elif "only delete your own" in result.message:
            raise PermissionDeniedException(message=result.message)
        else:
            raise InvalidInputException(message=result.message)
    return result


@router.get("/posts/{post_id}/engagement", response_model=PostEngagementResponse)
async def get_post_engagement(
    post_id: str,
    limit_comments: int = Query(5, ge=1, le=20, description="Number of recent comments"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get engagement data for a post (likes, comments, user's like status).
    
    **Path Parameters:**
    - `post_id`: UUID of the post
    
    **Query Parameters:**
    - `limit_comments`: Number of recent comments to include (default: 5)
    
    **Features:**
    - Returns like/comment counts
    - Indicates if current user has liked the post (if authenticated)
    - Includes recent comments with timestamps
    """
    current_user_id = str(current_user.id) if current_user else None
    result = await engagement_service.get_post_engagement(
        post_id, current_user_id, db, limit_comments
    )
    if not result:
        raise NotFoundException(message="Post not found")
    return result