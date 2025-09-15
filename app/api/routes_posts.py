from fastapi import APIRouter, Depends, Form, File, UploadFile, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json

from app.db.session import get_async_db
from app.services.post_service import post_service
from app.schemas.posts import PostCreate, PostUploadResponse, PostMediaCreate, PostListResponse, PostResponse
from app.auth.security import get_current_user, get_optional_current_user, verify_api_key
from src.models import User
from app.core.exceptions import InvalidInputException, NotFoundException

router = APIRouter(prefix="/api", tags=["posts"])


@router.post("/posts", response_model=PostUploadResponse)
async def create_post(
    caption: Optional[str] = Form(None, description="Post caption"),
    tags: Optional[str] = Form(None, description="JSON array of tags"),
    location_id: Optional[str] = Form(None, description="Location ID (UUID)"),
    lat: Optional[float] = Form(None, description="Latitude"),
    lng: Optional[float] = Form(None, description="Longitude"),
    media_files: List[UploadFile] = File(..., description="Media files (images/videos)"),
    db: AsyncSession = Depends(get_async_db),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_actor_id: Optional[str] = Header(None, alias="X-Actor-Id"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Create a new post with media uploads.
    
    **Authentication:**
    - Requires either valid JWT token or API key in X-API-Key header
    - If using API key, provide X-Actor-Id header for user identification
    
    **Multipart form data with:**
    - `caption`: Optional post caption (max 2000 chars)
    - `tags`: JSON array of tags (e.g., '["beach", "sunset"]')
    - `location_id`: Optional location UUID
    - `lat`, `lng`: Optional coordinates for auto-location matching
    - `media_files`: One or more image/video files
    
    **Features:**
    - Auto-location matching based on coordinates (5km radius)
    - Support for multiple media files
    - Tag processing and indexing
    - Structured logging for analytics
    
    **Location Matching:**
    If coordinates are provided, the system automatically finds
    the nearest location within 5km radius and associates it with the post.
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
    # Parse tags from JSON string
    parsed_tags = []
    if tags:
        try:
            parsed_tags = json.loads(tags)
            if not isinstance(parsed_tags, list):
                raise ValueError("Tags must be a JSON array")
        except (json.JSONDecodeError, ValueError):
            raise InvalidInputException(message="Invalid tags format. Must be JSON array.")

    # Process media files (in a real implementation, you'd upload to cloud storage)
    media_list = []
    for i, file in enumerate(media_files):
        # Validate file type
        if not file.content_type or not (
            file.content_type.startswith('image/') or
            file.content_type.startswith('video/')
        ):
            raise InvalidInputException(
                message=f"File {file.filename} must be an image or video"
            )
        
        # TODO: Upload to cloud storage (S3, GCS, etc.)
        # For now, create dummy URLs
        media_type = "image" if file.content_type.startswith('image/') else "video"
        fake_url = f"https://storage.example.com/posts/{actor_id}/{file.filename}"
        fake_thumb_url = f"https://storage.example.com/posts/{actor_id}/thumb_{file.filename}" if media_type == "video" else None
        
        media_list.append(PostMediaCreate(
            media_type=media_type,
            url=fake_url,
            thumb_url=fake_thumb_url,
            ordering=i
        ))

    if not media_list:
        raise InvalidInputException(message="At least one media file is required")

    # Create post data
    post_data = PostCreate(
        caption=caption,
        tags=parsed_tags,
        location_id=location_id,
        lat=lat,
        lng=lng,
        media=media_list
    )

    # Create post
    result = await post_service.create_post(post_data, actor_id, db)
    return result


@router.get("/posts", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Number of posts per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all posts with pagination, newest first.
    
    **Query Parameters:**
    - `page`: Page number (starting from 1)
    - `page_size`: Number of posts per page (1-50)
    
    **Features:**
    - Posts are returned in descending order by creation date (newest first)
    - Includes pagination metadata (total count, total pages, etc.)
    - Each post includes like count, comment count, and media information
    """
    result = await post_service.get_posts(db, page, page_size)
    return result


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_by_id(
    post_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a specific post by ID.
    
    **Path Parameters:**
    - `post_id`: UUID of the post to retrieve
    
    **Features:**
    - Returns complete post information including engagement metrics
    - Includes associated media and location data
    """
    post = await post_service.get_post_by_id(post_id, db)
    if not post:
        raise NotFoundException(message="Post not found")
    return post