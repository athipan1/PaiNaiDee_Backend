from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_async_db
from app.services.search_service import search_service
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_posts_get(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    lat: Optional[float] = Query(None, description="Latitude for distance-based sorting"),
    lon: Optional[float] = Query(None, description="Longitude for distance-based sorting"), 
    radius_km: Optional[float] = Query(50.0, description="Search radius in kilometers"),
    limit: int = Query(20, description="Number of results", ge=1, le=100),
    offset: int = Query(0, description="Pagination offset", ge=0),
    sort: Optional[str] = Query("relevance", description="Sort order: relevance, distance, popularity, newest"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search for travel posts using fuzzy matching, keyword expansion, and ranking.
    
    This endpoint implements Phase 1 contextual search with:
    - Fuzzy matching on location names and aliases using trigram similarity
    - Keyword expansion via static mapping (province → landmarks)
    - Post retrieval using expansion terms (caption ILIKE, tags overlap, location match)
    - Ranking blend (popularity + recency) with configurable weights
    - Distance-based filtering and sorting when lat/lon provided
    
    **Example queries:**
    - `?q=เชียงใหม่` - Searches for Chiang Mai and related landmarks
    - `?q=ทะเล&lat=7.8804&lon=98.3923&sort=distance` - Beach content near Phuket
    - `?q=ภูเขา&sort=popularity` - Popular mountain content
    """
    result = await search_service.search_posts(
        query=q,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        limit=limit,
        offset=offset,
        sort=sort,
        db=db
    )
    return result


@router.post("/search", response_model=SearchResponse)
async def search_posts_post(
    request: SearchRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search for travel posts using JSON request body (alternative to GET).
    
    This endpoint provides the same functionality as GET /search but accepts
    parameters via JSON request body for complex queries.
    
    **Example request body:**
    ```json
    {
        "q": "เชียงใหม่",
        "lat": 18.7883,
        "lon": 98.9853,
        "radius_km": 50,
        "limit": 20,
        "offset": 0,
        "sort": "distance"
    }
    ```
    """
    result = await search_service.search_posts(
        query=request.q,
        lat=request.lat,
        lon=request.lon,
        radius_km=request.radius_km,
        limit=request.limit,
        offset=request.offset,
        sort=request.sort,
        db=db
    )
    return result