from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from sqlalchemy.orm import selectinload
import uuid

from app.db.models import Location, Post
from app.utils.ranking import haversine_distance
from app.schemas.locations import (
    LocationResponse, LocationDetailResponse, NearbyLocationResponse, AutocompleteLocationResponse
)
from app.core.config import settings
from app.core.logging import logger


class LocationService:
    """Service for location-related operations"""
    
    async def get_location_by_id(
        self,
        location_id: str,
        db: AsyncSession
    ) -> Optional[LocationDetailResponse]:
        """
        Get location details by ID
        
        Args:
            location_id: Location UUID
            db: Database session
            
        Returns:
            LocationDetailResponse or None
        """
        try:
            location_uuid = uuid.UUID(location_id)
        except ValueError:
            return None
        
        # Get location with post count
        query = select(Location).where(Location.id == location_uuid)
        result = await db.execute(query)
        location = result.scalar_one_or_none()
        
        if not location:
            return None
        
        # Get posts count
        posts_count_query = select(func.count(Post.id)).where(Post.location_id == location.id)
        posts_count_result = await db.execute(posts_count_query)
        posts_count = posts_count_result.scalar() or 0
        
        return LocationDetailResponse(
            id=str(location.id),
            name=location.name,
            province=location.province,
            aliases=location.aliases or [],
            lat=location.lat,
            lng=location.lng,
            popularity_score=location.popularity_score,
            created_at=location.created_at,
            posts_count=posts_count,
            nearby_locations=[]  # Will be populated by get_nearby_locations
        )
    
    async def get_nearby_locations(
        self,
        location_id: str,
        radius_km: float,
        db: AsyncSession
    ) -> Optional[NearbyLocationResponse]:
        """
        Get nearby locations within radius
        
        Args:
            location_id: Center location UUID
            radius_km: Search radius in kilometers
            db: Database session
            
        Returns:
            NearbyLocationResponse or None
        """
        try:
            location_uuid = uuid.UUID(location_id)
        except ValueError:
            return None
        
        # Get center location
        center_query = select(Location).where(Location.id == location_uuid)
        center_result = await db.execute(center_query)
        center_location = center_result.scalar_one_or_none()
        
        if not center_location:
            return None
        
        # Log the request
        logger.location_nearby_request(
            location_id=location_id,
            radius_km=radius_km,
            result_count=0  # Will update after getting results
        )
        
        nearby_locations = []
        
        if center_location.lat is not None and center_location.lng is not None:
            # Use actual geographic distance
            nearby_locations = await self._find_nearby_by_distance(
                center_lat=center_location.lat,
                center_lng=center_location.lng,
                radius_km=radius_km,
                exclude_id=center_location.id,
                db=db
            )
        else:
            # Fallback: use curated list based on province or name similarity
            nearby_locations = await self._find_nearby_by_similarity(
                center_location=center_location,
                limit=20,
                db=db
            )
        
        # Convert to response format
        location_responses = [
            LocationResponse(
                id=str(loc.id),
                name=loc.name,
                province=loc.province,
                aliases=loc.aliases or [],
                lat=loc.lat,
                lng=loc.lng,
                popularity_score=loc.popularity_score,
                created_at=loc.created_at
            )
            for loc in nearby_locations
        ]
        
        # Update log with actual result count
        logger.location_nearby_request(
            location_id=location_id,
            radius_km=radius_km,
            result_count=len(location_responses)
        )
        
        return NearbyLocationResponse(
            locations=location_responses,
            radius_km=radius_km,
            total_count=len(location_responses)
        )
    
    async def _find_nearby_by_distance(
        self,
        center_lat: float,
        center_lng: float,
        radius_km: float,
        exclude_id: uuid.UUID,
        db: AsyncSession
    ) -> List[Location]:
        """Find nearby locations using geographic distance"""
        
        # Use PostGIS if available, otherwise Haversine formula
        distance_query = text("""
            SELECT *, 
            (6371 * acos(
                cos(radians(:center_lat)) * 
                cos(radians(lat)) * 
                cos(radians(lng) - radians(:center_lng)) + 
                sin(radians(:center_lat)) * 
                sin(radians(lat))
            )) AS distance_km
            FROM locations 
            WHERE lat IS NOT NULL 
              AND lng IS NOT NULL
              AND id != :exclude_id
            HAVING distance_km <= :radius_km
            ORDER BY distance_km
            LIMIT 50
        """)
        
        result = await db.execute(
            distance_query,
            {
                "center_lat": center_lat,
                "center_lng": center_lng,
                "radius_km": radius_km,
                "exclude_id": exclude_id
            }
        )
        
        # Convert to Location objects
        locations = []
        for row in result.fetchall():
            location = Location()
            location.id = row.id
            location.name = row.name
            location.province = row.province
            location.aliases = row.aliases
            location.lat = row.lat
            location.lng = row.lng
            location.popularity_score = row.popularity_score
            location.created_at = row.created_at
            locations.append(location)
        
        return locations
    
    async def _find_nearby_by_similarity(
        self,
        center_location: Location,
        limit: int,
        db: AsyncSession
    ) -> List[Location]:
        """Find nearby locations using similarity (fallback)"""
        
        # First try same province
        query = select(Location).where(
            and_(
                Location.id != center_location.id,
                Location.province == center_location.province
            )
        ).order_by(Location.popularity_score.desc()).limit(limit)
        
        result = await db.execute(query)
        locations = result.scalars().all()
        
        # If not enough results, add name similarity matches
        if len(locations) < limit // 2:
            similarity_query = text("""
                SELECT * FROM locations 
                WHERE id != :exclude_id
                  AND similarity(name, :center_name) > 0.2
                ORDER BY similarity(name, :center_name) DESC
                LIMIT :remaining_limit
            """)
            
            similarity_result = await db.execute(
                similarity_query,
                {
                    "exclude_id": center_location.id,
                    "center_name": center_location.name,
                    "remaining_limit": limit - len(locations)
                }
            )
            
            # Convert to Location objects and add to results
            for row in similarity_result.fetchall():
                location = Location()
                location.id = row.id
                location.name = row.name
                location.province = row.province
                location.aliases = row.aliases
                location.lat = row.lat
                location.lng = row.lng
                location.popularity_score = row.popularity_score
                location.created_at = row.created_at
                locations.append(location)
        
        return list(locations)
    
    async def autocomplete_locations(
        self,
        query: str,
        limit: int = 10,
        db: AsyncSession = None
    ) -> AutocompleteLocationResponse:
        """
        Get location autocomplete suggestions
        
        Args:
            query: Search query
            limit: Maximum number of suggestions
            db: Database session
            
        Returns:
            AutocompleteLocationResponse
        """
        # Use fuzzy search with trigrams
        autocomplete_query = text("""
            SELECT *, similarity(name, :query) as sim_score
            FROM locations 
            WHERE 
                name ILIKE :pattern
                OR similarity(name, :query) > 0.3
                OR EXISTS (
                    SELECT 1 FROM unnest(aliases) as alias
                    WHERE alias ILIKE :pattern OR similarity(alias, :query) > 0.3
                )
            ORDER BY 
                CASE WHEN name ILIKE :exact_pattern THEN 1 ELSE 2 END,
                sim_score DESC,
                popularity_score DESC
            LIMIT :limit
        """)
        
        result = await db.execute(
            autocomplete_query,
            {
                "query": query,
                "pattern": f"{query}%",
                "exact_pattern": f"{query}",
                "limit": limit
            }
        )
        
        # Convert to response format
        suggestions = []
        for row in result.fetchall():
            suggestions.append(LocationResponse(
                id=str(row.id),
                name=row.name,
                province=row.province,
                aliases=row.aliases or [],
                lat=row.lat,
                lng=row.lng,
                popularity_score=row.popularity_score,
                created_at=row.created_at
            ))
        
        return AutocompleteLocationResponse(
            suggestions=suggestions,
            query=query,
            total_count=len(suggestions)
        )
    
    async def list_locations(
        self,
        province: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: Optional[float] = 50.0,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None
    ) -> "LocationListResponse":
        """
        List locations with optional filtering and geographic proximity
        
        Args:
            province: Filter by province
            lat: User latitude for distance calculation
            lon: User longitude for distance calculation
            radius_km: Maximum distance from user coordinates
            limit: Number of results to return
            offset: Offset for pagination
            db: Database session
            
        Returns:
            LocationListResponse
        """
        from app.schemas.locations import LocationListResponse
        
        has_location = lat is not None and lon is not None
        
        # Build base query
        base_query = select(Location)
        count_query = select(func.count(Location.id))
        
        # Add province filter if specified
        if province:
            base_query = base_query.where(Location.province == province)
            count_query = count_query.where(Location.province == province)
        
        # Add geographic filter if coordinates provided
        if has_location and radius_km:
            from app.core.config import settings
            if "postgresql" in settings.database_uri:
                # PostgreSQL with PostGIS or Haversine calculation
                distance_condition = text(f"""
                    6371 * ACOS(
                        COS(RADIANS({lat})) * COS(RADIANS(lat)) * 
                        COS(RADIANS(lng) - RADIANS({lon})) + 
                        SIN(RADIANS({lat})) * SIN(RADIANS(lat))
                    ) <= {radius_km}
                """)
                base_query = base_query.where(distance_condition)
                count_query = count_query.where(distance_condition)
            else:
                # Simplified filtering for SQLite (approximate)
                lat_range = radius_km / 111.0  # Rough degrees per km
                lon_range = radius_km / (111.0 * abs(float(lat) if lat else 0) * 0.017453293)  # Adjust for latitude
                
                base_query = base_query.where(
                    Location.lat.between(lat - lat_range, lat + lat_range)
                ).where(
                    Location.lng.between(lon - lon_range, lon + lon_range)
                )
                count_query = count_query.where(
                    Location.lat.between(lat - lat_range, lat + lat_range)
                ).where(
                    Location.lng.between(lon - lon_range, lon + lon_range)
                )
        
        # Get total count
        total_result = await db.execute(count_query)
        total_count = total_result.scalar() or 0
        
        # Add ordering
        if has_location:
            # Order by distance if coordinates provided
            if "postgresql" in settings.database_uri:
                distance_calc = text(f"""
                    6371 * ACOS(
                        COS(RADIANS({lat})) * COS(RADIANS(lat)) * 
                        COS(RADIANS(lng) - RADIANS({lon})) + 
                        SIN(RADIANS({lat})) * SIN(RADIANS(lat))
                    )
                """)
                base_query = base_query.order_by(distance_calc)
            else:
                # For SQLite, order by simple distance approximation
                base_query = base_query.order_by(
                    ((Location.lat - lat)**2 + (Location.lng - lon)**2)
                )
        else:
            # Order by popularity and name
            base_query = base_query.order_by(Location.popularity_score.desc(), Location.name)
        
        # Add pagination
        base_query = base_query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(base_query)
        locations = result.scalars().all()
        
        # Get post counts for each location
        location_responses = []
        for location in locations:
            posts_count_query = select(func.count(Post.id)).where(Post.location_id == location.id)
            posts_count_result = await db.execute(posts_count_query)
            posts_count = posts_count_result.scalar() or 0
            
            # Calculate distance if coordinates provided
            distance_km = None
            if has_location and location.lat and location.lng:
                distance_km = haversine_distance(lat, lon, location.lat, location.lng)
            
            location_responses.append(LocationResponse(
                id=str(location.id),
                name=location.name,
                province=location.province,
                aliases=location.aliases.split(',') if location.aliases else [],
                lat=location.lat,
                lng=location.lng,
                popularity_score=location.popularity_score,
                created_at=location.created_at,
                distance_km=distance_km,
                posts_count=posts_count
            ))
        
        # Build filters info
        filters = {}
        if province:
            filters["province"] = province
        if has_location:
            filters["coordinates"] = {"lat": lat, "lon": lon, "radius_km": radius_km}
        
        return LocationListResponse(
            locations=location_responses,
            total_count=total_count,
            has_more=(offset + len(location_responses)) < total_count,
            filters=filters
        )


# Global service instance
location_service = LocationService()