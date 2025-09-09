from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.services.search_service import search_service
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_posts(
    request: SearchRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Search for travel posts using fuzzy matching, keyword expansion, and ranking.
    
    This endpoint implements Phase 1 contextual search with:
    - Fuzzy matching on location names and aliases using trigram similarity
    - Keyword expansion via static mapping (province → landmarks)
    - Post retrieval using expansion terms (caption ILIKE, tags overlap, location match)
    - Ranking blend (popularity + recency) with configurable weights
    
    **Example queries in request body:**
    - `{"q": "เชียงใหม่"}` - Searches for Chiang Mai and related landmarks
    - `{"q": "ทะเล"}` - Searches for sea/beach related content
    - `{"q": "ภูเขา"}` - Searches for mountain/hill related content
    """
    result = await search_service.search_posts(
        query=request.q,
        limit=request.limit,
        offset=request.offset,
        db=db
    )
    return result