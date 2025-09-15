from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_async_db
from app.services.location_service import location_service
from app.schemas.locations import (
    LocationDetailResponse, NearbyLocationResponse, AutocompleteLocationResponse,
    LocationListResponse
)
from app.schemas.search import NearbyRequest

router = APIRouter(prefix="/api", tags=["locations"])


@router.get("/locations", response_model=LocationListResponse)
async def get_locations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of locations per page"),
    province: Optional[str] = Query(None, description="Filter by province"),
    lat: Optional[float] = Query(None, description="Latitude for distance filtering"),
    lon: Optional[float] = Query(None, description="Longitude for distance filtering"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers", ge=0.1, le=500.0),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all locations with pagination and optional filtering.
    
    **Query Parameters:**
    - `page`: Page number (starting from 1)
    - `page_size`: Number of locations per page (1-100)
    - `province`: Filter by province name
    - `lat`, `lon`, `radius_km`: Geographic filtering
    
    **Features:**
    - Pagination with metadata (total count, total pages, etc.)
    - Geographic filtering when coordinates provided
    - Province-based filtering
    - Results ordered by popularity score
    """
    result = await location_service.get_locations(
        page=page,
        page_size=page_size,
        province=province,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        db=db
    )
    return result


@router.get("/locations/{location_id}", response_model=LocationDetailResponse)
async def get_location(
    location_id: str = Path(..., description="Location ID (UUID)"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get detailed information about a specific location.
    
    Returns location details including:
    - Basic location information (name, province, coordinates)
    - Aliases and popularity score
    - Number of associated posts
    """
    location = await location_service.get_location_by_id(location_id, db)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.get("/locations/{location_id}/nearby", response_model=NearbyLocationResponse)
async def get_nearby_locations(
    location_id: str = Path(..., description="Location ID (UUID)"),
    radius_km: float = Query(default=10.0, ge=0.1, le=100.0, description="Search radius in kilometers"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get nearby locations within specified radius.
    
    Uses geographic distance calculation if coordinates are available,
    otherwise falls back to curated list based on province or name similarity.
    
    **Features:**
    - Geographic distance calculation using Haversine formula
    - Fallback to province-based similarity matching
    - Configurable search radius (0.1-100 km)
    - Results ordered by distance or relevance
    """
    nearby = await location_service.get_nearby_locations(location_id, radius_km, db)
    if not nearby:
        raise HTTPException(status_code=404, detail="Location not found")
    return nearby


@router.get("/locations/autocomplete", response_model=AutocompleteLocationResponse)
async def autocomplete_locations(
    q: str = Query(..., description="Search query for autocomplete", min_length=1),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of suggestions"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get location autocomplete suggestions.
    
    Provides fast location suggestions using:
    - Prefix matching for exact matches
    - Fuzzy matching using trigram similarity
    - Alias matching for alternative names
    - Popularity-based ranking
    
    **Use cases:**
    - Search box autocomplete
    - Location picker suggestions
    - Quick location lookup
    """
    try:
        result = await location_service.autocomplete_locations(q, limit, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocomplete failed: {str(e)}")