from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func, and_, or_
from sqlalchemy.orm import selectinload
import time
import asyncio

from app.db.models import Location, Post, PostMedia
from app.utils.text_normalize import normalize_text, expand_query_terms
from app.utils.expansion_loader import expansion_loader
from app.utils.ranking import calculate_combined_score
from app.schemas.search import SearchResponse, PostResponse, MediaResponse, LocationResponse, SuggestionResponse
from app.core.logging import logger
from app.core.config import settings


class SearchService:
    """Advanced search service with fuzzy matching and ranking"""
    
    def __init__(self):
        self.trigram_threshold = settings.trigram_sim_threshold
    
    async def search_posts(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None
    ) -> SearchResponse:
        """
        Main search method for posts with fuzzy matching and ranking
        
        Args:
            query: Search query
            limit: Number of results to return
            offset: Offset for pagination
            db: Database session
            
        Returns:
            SearchResponse with results
        """
        start_time = time.time()
        
        # Normalize query
        normalized_query = normalize_text(query)
        
        # Expand query terms
        expanded_terms = expansion_loader.expand_query(query)
        expansion_list = list(expanded_terms - {query})  # Remove original query
        
        # Find matching locations using fuzzy search
        location_ids = await self._find_matching_locations(normalized_query, db)
        
        # Build comprehensive search for posts
        posts_with_scores = await self._search_posts_with_ranking(
            query=normalized_query,
            expanded_terms=expanded_terms,
            location_ids=location_ids,
            limit=limit,
            offset=offset,
            db=db
        )
        
        # Convert to response format
        post_responses = []
        for post, score in posts_with_scores:
            media_responses = [
                MediaResponse(
                    type=media.media_type,
                    url=media.url,
                    thumb_url=media.thumb_url
                )
                for media in post.media
            ]
            
            location_response = None
            if post.location:
                location_response = LocationResponse(
                    id=str(post.location.id),
                    name=post.location.name,
                    province=post.location.province,
                    lat=post.location.lat,
                    lng=post.location.lng
                )
            
            post_responses.append(PostResponse(
                id=str(post.id),
                caption=post.caption,
                media=media_responses,
                location=location_response,
                like_count=post.like_count,
                comment_count=post.comment_count,
                created_at=post.created_at,
                score=score
            ))
        
        # Generate suggestions
        suggestions = await self._generate_suggestions(query, db)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Log search event
        logger.search_performed(
            query=query,
            normalized=normalized_query,
            result_count=len(post_responses),
            latency_ms=latency_ms
        )
        
        return SearchResponse(
            query=query,
            expansion=expansion_list,
            posts=post_responses,
            suggestions=suggestions,
            latency_ms=latency_ms
        )
    
    async def _find_matching_locations(
        self,
        query: str,
        db: AsyncSession
    ) -> List[str]:
        """Find locations using trigram similarity"""
        # Use pg_trgm for fuzzy matching
        similarity_query = text("""
            SELECT id::text, name, similarity(name, :query) as sim_score
            FROM locations 
            WHERE similarity(name, :query) > :threshold
               OR EXISTS (
                   SELECT 1 FROM unnest(aliases) as alias
                   WHERE similarity(alias, :query) > :threshold
               )
            ORDER BY sim_score DESC
            LIMIT 50
        """)
        
        result = await db.execute(
            similarity_query,
            {
                "query": query,
                "threshold": self.trigram_threshold
            }
        )
        
        location_ids = [row[0] for row in result.fetchall()]
        return location_ids
    
    async def _search_posts_with_ranking(
        self,
        query: str,
        expanded_terms: set,
        location_ids: List[str],
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Tuple[Post, float]]:
        """Search posts with comprehensive ranking"""
        
        # Convert expanded terms to list for SQL
        terms_list = list(expanded_terms)
        
        # Build dynamic SQL for post search with ranking
        search_sql = text("""
            WITH post_matches AS (
                SELECT 
                    p.*,
                    CASE 
                        WHEN p.caption ILIKE ANY(:caption_terms) THEN 0.8
                        WHEN p.tags && :tags_array THEN 0.7
                        WHEN p.location_id = ANY(:location_ids) THEN 0.9
                        ELSE 0.5
                    END as relevance_score,
                    -- Popularity normalization (simple logarithmic)
                    LOG(1 + p.like_count + :alpha_comment * p.comment_count) / LOG(1001) as popularity_norm,
                    -- Recency decay (exponential)
                    EXP(-EXTRACT(EPOCH FROM (NOW() - p.created_at)) / 60.0 / :tau_minutes) as recency_decay
                FROM posts p
                WHERE 
                    p.caption ILIKE ANY(:caption_terms)
                    OR p.tags && :tags_array
                    OR p.location_id = ANY(:location_ids)
            )
            SELECT 
                *,
                (:w_pop * popularity_norm + :w_recency * recency_decay) * relevance_score as combined_score
            FROM post_matches
            ORDER BY combined_score DESC
            LIMIT :limit OFFSET :offset
        """)
        
        # Prepare parameters
        caption_terms = [f"%{term}%" for term in terms_list]
        weights = settings.search_weights
        location_ids_list = location_ids if location_ids else [None]
        
        result = await db.execute(
            search_sql,
            {
                "caption_terms": caption_terms,
                "tags_array": terms_list,
                "location_ids": location_ids_list,
                "alpha_comment": settings.alpha_comment,
                "tau_minutes": settings.tau_minutes,
                "w_pop": weights.get("w_pop", 0.7),
                "w_recency": weights.get("w_recency", 0.3),
                "limit": limit,
                "offset": offset
            }
        )
        
        # Get post IDs and scores
        post_data = result.fetchall()
        if not post_data:
            return []
        
        post_ids = [str(row.id) for row in post_data]
        scores = {str(row.id): row.combined_score for row in post_data}
        
        # Fetch full post objects with relationships
        posts_query = select(Post).options(
            selectinload(Post.media),
            selectinload(Post.location)
        ).where(Post.id.in_(post_ids))
        
        posts_result = await db.execute(posts_query)
        posts = posts_result.scalars().all()
        
        # Combine posts with scores and maintain order
        posts_with_scores = [(post, scores[str(post.id)]) for post in posts]
        posts_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        return posts_with_scores
    
    async def _generate_suggestions(
        self,
        query: str,
        db: AsyncSession
    ) -> List[SuggestionResponse]:
        """Generate search suggestions"""
        suggestions = []
        
        # Add province suggestions
        matching_provinces = expansion_loader.find_matching_provinces(query)
        for province in matching_provinces[:3]:  # Limit to 3
            suggestions.append(SuggestionResponse(
                type="place",
                text=province
            ))
        
        # Add category suggestions
        query_lower = query.lower()
        categories = ["ทะเล", "ภูเขา", "วัด", "ธรรมชาติ", "อาหาร"]
        for category in categories:
            if query_lower in category.lower():
                suggestions.append(SuggestionResponse(
                    type="category",
                    text=category
                ))
        
        return suggestions


# Global service instance
search_service = SearchService()