from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_async_db
from app.services.search_service import search_service
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_posts(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    limit: int = Query(default=20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search for travel posts using fuzzy matching, keyword expansion, and ranking.

    This endpoint implements Phase 1 contextual search with:
    - Fuzzy matching on location names and aliases using trigram similarity
    - Keyword expansion via static mapping (province → landmarks)
    - Post retrieval using expansion terms (caption ILIKE, tags overlap, location match)
    - Ranking blend (popularity + recency) with configurable weights

    **Example queries:**
    - `เชียงใหม่` - Searches for Chiang Mai and related landmarks
    - `ทะเล` - Searches for sea/beach related content
    - `ภูเขา` - Searches for mountain/hill related content
    """
    try:
        result = await search_service.search_posts(
            query=q,
            limit=limit,
            offset=offset,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
