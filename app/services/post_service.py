from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, and_
import uuid

from app.db.models import Post, PostMedia, Location
from app.utils.ranking import haversine_distance
from app.schemas.posts import PostCreate, PostResponse, PostUploadResponse, PostMediaCreate
from app.core.logging import logger


class PostService:
    """Service for post-related operations"""
    
    async def create_post(
        self,
        post_data: PostCreate,
        user_id: str,  # TODO: Extract from auth token
        db: AsyncSession
    ) -> PostUploadResponse:
        """
        Create a new post with media and optional location matching
        
        Args:
            post_data: Post creation data
            user_id: User ID (from auth)
            db: Database session
            
        Returns:
            PostUploadResponse
        """
        # Create post
        post = Post(
            user_id=user_id,
            caption=post_data.caption,
            tags=post_data.tags or [],
            lat=post_data.lat,
            lng=post_data.lng
        )
        
        # Auto-match location if coordinates provided
        location_matched = None
        if post_data.lat is not None and post_data.lng is not None:
            matched_location = await self._find_nearest_location(
                lat=post_data.lat,
                lng=post_data.lng,
                max_distance_km=5.0,  # 5km radius for auto-matching
                db=db
            )
            if matched_location:
                post.location_id = matched_location.id
                location_matched = matched_location.name
        elif post_data.location_id:
            # Use provided location_id
            try:
                location_uuid = uuid.UUID(post_data.location_id)
                post.location_id = location_uuid
                
                # Get location name for response
                location_query = select(Location).where(Location.id == location_uuid)
                location_result = await db.execute(location_query)
                location = location_result.scalar_one_or_none()
                if location:
                    location_matched = location.name
            except ValueError:
                pass  # Invalid UUID, ignore
        
        db.add(post)
        await db.flush()  # Get the post ID
        
        # Create media entries
        for media_data in post_data.media:
            post_media = PostMedia(
                post_id=post.id,
                media_type=media_data.media_type,
                url=media_data.url,
                thumb_url=media_data.thumb_url,
                ordering=media_data.ordering
            )
            db.add(post_media)
        
        await db.commit()
        await db.refresh(post)
        
        # Log the upload event
        logger.post_uploaded(
            post_id=str(post.id),
            has_geo=post.lat is not None and post.lng is not None,
            location_matched=location_matched
        )
        
        # Convert to response
        post_response = PostResponse(
            id=str(post.id),
            user_id=post.user_id,
            caption=post.caption,
            tags=post.tags or [],
            location_id=str(post.location_id) if post.location_id else None,
            lat=post.lat,
            lng=post.lng,
            like_count=post.like_count,
            comment_count=post.comment_count,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        
        return PostUploadResponse(
            success=True,
            post=post_response,
            location_matched=location_matched,
            message="Post created successfully"
        )
    
    async def _find_nearest_location(
        self,
        lat: float,
        lng: float,
        max_distance_km: float,
        db: AsyncSession
    ) -> Optional[Location]:
        """
        Find the nearest location within max_distance_km
        
        Args:
            lat: Latitude
            lng: Longitude
            max_distance_km: Maximum distance in kilometers
            db: Database session
            
        Returns:
            Nearest Location or None
        """
        # Use geographic distance calculation
        distance_query = text("""
            SELECT *, 
            (6371 * acos(
                cos(radians(:lat)) * 
                cos(radians(lat)) * 
                cos(radians(lng) - radians(:lng)) + 
                sin(radians(:lat)) * 
                sin(radians(lat))
            )) AS distance_km
            FROM locations 
            WHERE lat IS NOT NULL 
              AND lng IS NOT NULL
            HAVING distance_km <= :max_distance
            ORDER BY distance_km
            LIMIT 1
        """)
        
        result = await db.execute(
            distance_query,
            {
                "lat": lat,
                "lng": lng,
                "max_distance": max_distance_km
            }
        )
        
        row = result.fetchone()
        if not row:
            return None
        
        # Convert to Location object
        location = Location()
        location.id = row.id
        location.name = row.name
        location.province = row.province
        location.aliases = row.aliases
        location.lat = row.lat
        location.lng = row.lng
        location.popularity_score = row.popularity_score
        location.created_at = row.created_at
        
        return location
    
    async def get_post_by_id(
        self,
        post_id: str,
        db: AsyncSession
    ) -> Optional[PostResponse]:
        """
        Get post by ID
        
        Args:
            post_id: Post UUID
            db: Database session
            
        Returns:
            PostResponse or None
        """
        try:
            post_uuid = uuid.UUID(post_id)
        except ValueError:
            return None
        
        query = select(Post).where(Post.id == post_uuid)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            return None
        
        return PostResponse(
            id=str(post.id),
            user_id=post.user_id,
            caption=post.caption,
            tags=post.tags or [],
            location_id=str(post.location_id) if post.location_id else None,
            lat=post.lat,
            lng=post.lng,
            like_count=post.like_count,
            comment_count=post.comment_count,
            created_at=post.created_at,
            updated_at=post.updated_at
        )


# Global service instance
post_service = PostService()