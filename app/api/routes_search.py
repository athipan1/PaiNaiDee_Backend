from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_async_db
from app.services.search_service import search_service
from app.schemas.search import SearchRequest, SearchResponse, SortOption

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_posts_get(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude for distance calculation"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude for distance calculation"),
    radius_km: Optional[float] = Query(50.0, ge=0.1, le=500.0, description="Search radius in kilometers"),
    sort: SortOption = Query(SortOption.relevance, description="Sort order"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search for travel posts using fuzzy matching, keyword expansion, and ranking (GET version).
    
    This endpoint implements Phase 1 contextual search with:
    - Fuzzy matching on location names and aliases using trigram similarity
    - Keyword expansion via static mapping (province → landmarks)
    - Geographic filtering with Haversine distance calculations
    - Multi-dimensional ranking combining relevance, popularity, recency, and distance
    
    **Query Parameters:**
    - `q`: Search query (1-500 characters)
    - `lat`, `lon`: User location for distance-based filtering and sorting
    - `radius_km`: Search radius in kilometers (0.1-500, default: 50)
    - `sort`: Sort order - `relevance` (default), `distance`, `popularity`, `newest`
    - `limit`: Number of results (1-100, default: 20)
    - `offset`: Pagination offset (default: 0)
    
    **Sort Options:**
    - `relevance`: Combined score of text similarity + popularity + recency
    - `distance`: Nearest locations first (requires lat/lon)
    - `popularity`: Most liked/commented posts first
    - `newest`: Most recent posts first
    
    **Example queries:**
    - `/api/search?q=เชียงใหม่` - Search for Chiang Mai content
    - `/api/search?q=ทะเล&lat=13.7563&lon=100.5018&sort=distance` - Beach content near Bangkok
    - `/api/search?q=ภูเขา&sort=popularity` - Mountain content sorted by popularity
    """
    # Create search request from query parameters
    request = SearchRequest(
        q=q,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        sort=sort,
        limit=limit,
        offset=offset
    )
    
    result = await search_service.search_posts(
        query=request.q,
        lat=request.lat,
        lon=request.lon,
        radius_km=request.radius_km,
        sort=request.sort,
        limit=request.limit,
        offset=request.offset,
        db=db
    )
    return result


@router.post("/search", response_model=SearchResponse)
@router.post("/search", response_model=SearchResponse)
async def search_posts(
    request: SearchRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search for travel posts using fuzzy matching, keyword expansion, and ranking (POST version).
    
    This endpoint implements Phase 1 contextual search with:
    - Fuzzy matching on location names and aliases using trigram similarity
    - Keyword expansion via static mapping (province → landmarks)
    - Geographic filtering with Haversine distance calculations  
    - Multi-dimensional ranking combining relevance, popularity, recency, and distance
    
    **Request Body Example:**
    ```json
    {
        "q": "เชียงใหม่",
        "lat": 18.7883,
        "lon": 98.9853,
        "radius_km": 20.0,
        "sort": "distance",
        "limit": 10,
        "offset": 0
    }
    ```
    
    **Example queries:**
    - `{"q": "เชียงใหม่"}` - Searches for Chiang Mai and related landmarks
    - `{"q": "ทะเล", "sort": "popularity"}` - Sea/beach content sorted by popularity
    - `{"q": "ภูเขา", "lat": 18.0, "lon": 99.0, "sort": "distance"}` - Mountain content near user
    """
    result = await search_service.search_posts(
        query=request.q,
        lat=request.lat,
        lon=request.lon,
        radius_km=request.radius_km,
        sort=request.sort,
        limit=request.limit,
        offset=request.offset,
        db=db
    )
    return result