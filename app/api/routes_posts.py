from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json

from app.db.session import get_async_db
from app.services.post_service import post_service
from app.schemas.posts import PostCreate, PostUploadResponse, PostMediaCreate

router = APIRouter(prefix="/api", tags=["posts"])


def get_current_user_id() -> str:
    """
    TODO: Extract user ID from JWT token
    For now, return a dummy user ID for Phase 1 testing
    """
    return "user_123_demo"  # TODO: Replace with actual auth


def _parse_tags(tags: Optional[str]) -> List[str]:
    """Parse tags from JSON string."""
    if not tags:
        return []

    try:
        parsed_tags = json.loads(tags)
        if not isinstance(parsed_tags, list):
            raise ValueError("Tags must be a JSON array")
        return parsed_tags
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid tags format. Must be JSON array.")


def _validate_media_file(file: UploadFile) -> str:
    """Validate media file and return media type."""
    if not file.content_type or not (
        file.content_type.startswith('image/') or
        file.content_type.startswith('video/')
    ):
        raise HTTPException(
            status_code=400,
            detail=f"File {file.filename} must be an image or video"
        )
    return "image" if file.content_type.startswith('image/') else "video"


def _process_media_files(media_files: List[UploadFile], current_user_id: str) -> List[PostMediaCreate]:
    """Process media files and create media objects."""
    media_list = []
    for i, file in enumerate(media_files):
        media_type = _validate_media_file(file)

        # TODO: Upload to cloud storage (S3, GCS, etc.)
        # For now, create dummy URLs
        fake_url = f"https://storage.example.com/posts/{current_user_id}/{file.filename}"
        fake_thumb_url = f"https://storage.example.com/posts/{current_user_id}/thumb_{file.filename}" if media_type == "video" else None

        media_list.append(PostMediaCreate(
            media_type=media_type,
            url=fake_url,
            thumb_url=fake_thumb_url,
            ordering=i
        ))

    if not media_list:
        raise HTTPException(status_code=400, detail="At least one media file is required")

    return media_list


@router.post("/posts", response_model=PostUploadResponse)
async def create_post(
    caption: Optional[str] = Form(None, description="Post caption"),
    tags: Optional[str] = Form(None, description="JSON array of tags"),
    location_id: Optional[str] = Form(None, description="Location ID (UUID)"),
    lat: Optional[float] = Form(None, description="Latitude"),
    lng: Optional[float] = Form(None, description="Longitude"),
    media_files: List[UploadFile] = File(..., description="Media files (images/videos)"),
    db: AsyncSession = Depends(get_async_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new post with media uploads.

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
    try:
        # Parse tags and process media files
        parsed_tags = _parse_tags(tags)
        media_list = _process_media_files(media_files, current_user_id)

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
        result = await post_service.create_post(post_data, current_user_id, db)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post creation failed: {str(e)}")
