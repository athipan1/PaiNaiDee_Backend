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
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: Optional[float] = 50.0,
        sort: str = "relevance",
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None
    ) -> SearchResponse:
        """
        Main search method for posts with fuzzy matching, geographic filtering, and ranking
        
        Args:
            query: Search query
            lat: User latitude for distance calculation
            lon: User longitude for distance calculation
            radius_km: Search radius in kilometers
            sort: Sort order (relevance, distance, popularity, newest)
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
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            sort=sort,
            limit=limit,
            offset=offset,
            db=db
        )
        
        # Convert to response format
        post_responses = []
        for post, score, distance_km in posts_with_scores:
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
                score=score,
                distance_km=distance_km
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
        """Find locations using fuzzy matching (database-agnostic)"""
        from app.core.config import settings
        
        # Check if we're using PostgreSQL with pg_trgm
        if "postgresql" in settings.database_uri:
            # Use pg_trgm for fuzzy matching on PostgreSQL
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
        else:
            # Fallback to LIKE-based matching for SQLite
            like_pattern = f"%{query}%"
            similarity_query = text("""
                SELECT id, name
                FROM locations 
                WHERE name LIKE :pattern
                   OR (aliases IS NOT NULL AND aliases LIKE :pattern)
                ORDER BY 
                    CASE 
                        WHEN name = :exact_query THEN 3
                        WHEN name LIKE :pattern THEN 2
                        ELSE 1
                    END DESC,
                    length(name) ASC
                LIMIT 50
            """)
            
            result = await db.execute(
                similarity_query,
                {
                    "pattern": like_pattern,
                    "exact_query": query
                }
            )
        
        location_ids = [str(row[0]) for row in result.fetchall()]
        return location_ids
    
    async def _search_posts_with_ranking(
        self,
        query: str,
        expanded_terms: set,
        location_ids: List[str],
        lat: Optional[float],
        lon: Optional[float],
        radius_km: Optional[float],
        sort: str,
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Tuple[Post, float, Optional[float]]]:
        """Search posts with comprehensive ranking including geographic distance"""
        from app.core.config import settings
        
        # Convert expanded terms to list for SQL
        terms_list = list(expanded_terms)
        
        # Determine if we have location context for distance calculation
        has_location = lat is not None and lon is not None
        is_postgresql = "postgresql" in settings.database_uri
        
        # Build database-specific search query
        if is_postgresql:
            return await self._search_posts_postgresql(
                terms_list, location_ids, lat, lon, radius_km, sort, limit, offset, db
            )
        else:
            return await self._search_posts_sqlite(
                terms_list, location_ids, lat, lon, radius_km, sort, limit, offset, db
            )
        
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
        
        # Get post IDs, scores, and distances
        post_data = result.fetchall()
        if not post_data:
            return []
        
        post_ids = [str(row.id) for row in post_data]
        scores = {str(row.id): row.combined_score for row in post_data}
        distances = {str(row.id): getattr(row, 'distance_km', None) for row in post_data}
        
        # Fetch full post objects with relationships
        posts_query = select(Post).options(
            selectinload(Post.media),
            selectinload(Post.location)
        ).where(Post.id.in_(post_ids))
        
        posts_result = await db.execute(posts_query)
        posts = posts_result.scalars().all()
        
        # Combine posts with scores and distances and maintain order
        posts_with_scores = [
            (post, scores[str(post.id)], distances[str(post.id)]) 
            for post in posts
        ]
        
        # Sort according to the original sort order
        if sort == "distance" and has_location:
            posts_with_scores.sort(key=lambda x: (x[2] is None, x[2] or float('inf'), -x[1]))
        elif sort == "popularity":
            posts_with_scores.sort(key=lambda x: (-x[0].like_count - 2*x[0].comment_count, -x[1]))
        elif sort == "newest":
            posts_with_scores.sort(key=lambda x: (-x[0].created_at.timestamp(), -x[1]))
        else:  # relevance
            posts_with_scores.sort(key=lambda x: -x[1])
        
        return posts_with_scores
    
    async def _search_posts_postgresql(
        self,
        terms_list: List[str],
        location_ids: List[str],
        lat: Optional[float],
        lon: Optional[float],
        radius_km: Optional[float],
        sort: str,
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Tuple[Post, float, Optional[float]]]:
        """PostgreSQL-specific search with full features"""
        has_location = lat is not None and lon is not None
        
        # Build geographic distance calculation if coordinates provided
        distance_calc = ""
        distance_filter = ""
        if has_location:
            # Haversine distance formula in SQL
            distance_calc = f"""
                , CASE 
                    WHEN p.lat IS NOT NULL AND p.lng IS NOT NULL THEN
                        6371 * ACOS(
                            COS(RADIANS({lat})) * COS(RADIANS(p.lat)) * 
                            COS(RADIANS(p.lng) - RADIANS({lon})) + 
                            SIN(RADIANS({lat})) * SIN(RADIANS(p.lat))
                        )
                    WHEN l.lat IS NOT NULL AND l.lng IS NOT NULL THEN
                        6371 * ACOS(
                            COS(RADIANS({lat})) * COS(RADIANS(l.lat)) * 
                            COS(RADIANS(l.lng) - RADIANS({lon})) + 
                            SIN(RADIANS({lat})) * SIN(RADIANS(l.lat))
                        )
                    ELSE NULL
                END as distance_km
            """
            
            if radius_km:
                distance_filter = f"""
                    AND (
                        (p.lat IS NOT NULL AND p.lng IS NOT NULL AND
                         6371 * ACOS(
                            COS(RADIANS({lat})) * COS(RADIANS(p.lat)) * 
                            COS(RADIANS(p.lng) - RADIANS({lon})) + 
                            SIN(RADIANS({lat})) * SIN(RADIANS(p.lat))
                         ) <= {radius_km})
                        OR
                        (l.lat IS NOT NULL AND l.lng IS NOT NULL AND
                         6371 * ACOS(
                            COS(RADIANS({lat})) * COS(RADIANS(l.lat)) * 
                            COS(RADIANS(l.lng) - RADIANS({lon})) + 
                            SIN(RADIANS({lat})) * SIN(RADIANS(l.lat))
                         ) <= {radius_km})
                        OR
                        (p.lat IS NULL AND p.lng IS NULL AND l.lat IS NULL AND l.lng IS NULL)
                    )
                """
        else:
            distance_calc = ", NULL as distance_km"
        
        # Determine sort order
        sort_clause = "combined_score DESC"
        if sort == "distance" and has_location:
            sort_clause = "distance_km ASC NULLS LAST, combined_score DESC"
        elif sort == "popularity":
            sort_clause = "popularity_norm DESC, combined_score DESC"
        elif sort == "newest":
            sort_clause = "p.created_at DESC, combined_score DESC"
        
        # Build dynamic SQL for post search with ranking
        search_sql = text(f"""
            WITH post_matches AS (
                SELECT 
                    p.*,
                    l.name as location_name,
                    l.lat as location_lat,
                    l.lng as location_lng,
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
                    {distance_calc}
                FROM posts p
                LEFT JOIN locations l ON p.location_id = l.id
                WHERE 
                    (p.caption ILIKE ANY(:caption_terms)
                    OR p.tags && :tags_array
                    OR p.location_id = ANY(:location_ids))
                    {distance_filter}
            )
            SELECT 
                *,
                (:w_pop * popularity_norm + :w_recency * recency_decay) * relevance_score as combined_score
            FROM post_matches
            ORDER BY {sort_clause}
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
        
        return await self._process_search_results(result, sort, has_location, db)
    
    async def _search_posts_sqlite(
        self,
        terms_list: List[str],
        location_ids: List[str],
        lat: Optional[float],
        lon: Optional[float],
        radius_km: Optional[float],
        sort: str,
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Tuple[Post, float, Optional[float]]]:
        """SQLite-specific search with simplified features"""
        has_location = lat is not None and lon is not None
        
        # Build geographic distance calculation for SQLite
        distance_calc = ""
        distance_filter = ""
        if has_location:
            # Simplified distance calculation for SQLite (still accurate but simpler syntax)
            distance_calc = f"""
                , CASE 
                    WHEN p.lat IS NOT NULL AND p.lng IS NOT NULL THEN
                        6371 * 2 * ASIN(SQRT(
                            POWER(SIN(({lat} - p.lat) * 3.14159265359 / 180 / 2), 2) +
                            COS({lat} * 3.14159265359 / 180) * COS(p.lat * 3.14159265359 / 180) *
                            POWER(SIN(({lon} - p.lng) * 3.14159265359 / 180 / 2), 2)
                        ))
                    WHEN l.lat IS NOT NULL AND l.lng IS NOT NULL THEN
                        6371 * 2 * ASIN(SQRT(
                            POWER(SIN(({lat} - l.lat) * 3.14159265359 / 180 / 2), 2) +
                            COS({lat} * 3.14159265359 / 180) * COS(l.lat * 3.14159265359 / 180) *
                            POWER(SIN(({lon} - l.lng) * 3.14159265359 / 180 / 2), 2)
                        ))
                    ELSE NULL
                END as distance_km
            """
            
            if radius_km:
                distance_filter = f"""
                    AND (
                        (p.lat IS NOT NULL AND p.lng IS NOT NULL AND
                         6371 * 2 * ASIN(SQRT(
                            POWER(SIN(({lat} - p.lat) * 3.14159265359 / 180 / 2), 2) +
                            COS({lat} * 3.14159265359 / 180) * COS(p.lat * 3.14159265359 / 180) *
                            POWER(SIN(({lon} - p.lng) * 3.14159265359 / 180 / 2), 2)
                         )) <= {radius_km})
                        OR
                        (l.lat IS NOT NULL AND l.lng IS NOT NULL AND
                         6371 * 2 * ASIN(SQRT(
                            POWER(SIN(({lat} - l.lat) * 3.14159265359 / 180 / 2), 2) +
                            COS({lat} * 3.14159265359 / 180) * COS(l.lat * 3.14159265359 / 180) *
                            POWER(SIN(({lon} - l.lng) * 3.14159265359 / 180 / 2), 2)
                         )) <= {radius_km})
                        OR
                        (p.lat IS NULL AND p.lng IS NULL AND l.lat IS NULL AND l.lng IS NULL)
                    )
                """
        else:
            distance_calc = ", NULL as distance_km"
        
        # Build WHERE clauses for text search (SQLite-compatible)
        text_conditions = []
        if terms_list:
            text_conditions.extend([f"p.caption LIKE '%{term}%'" for term in terms_list])
        
        if location_ids:
            location_placeholders = ",".join([f"'{loc_id}'" for loc_id in location_ids if loc_id])
            if location_placeholders:
                text_conditions.append(f"p.location_id IN ({location_placeholders})")
        
        where_clause = " OR ".join(text_conditions) if text_conditions else "1=1"
        
        # Determine sort order
        sort_clause = "combined_score DESC"
        if sort == "distance" and has_location:
            sort_clause = "distance_km ASC, combined_score DESC"
        elif sort == "popularity":
            sort_clause = "popularity_norm DESC, combined_score DESC"
        elif sort == "newest":
            sort_clause = "p.created_at DESC, combined_score DESC"
        
        # Build dynamic SQL for post search with ranking (SQLite-compatible)
        search_sql = text(f"""
            WITH post_matches AS (
                SELECT 
                    p.*,
                    l.name as location_name,
                    l.lat as location_lat,
                    l.lng as location_lng,
                    CASE 
                        WHEN {" OR ".join([f"p.caption LIKE '%{term}%'" for term in terms_list]) if terms_list else "0=1"} THEN 0.8
                        WHEN p.location_id IN ({",".join([f"'{loc_id}'" for loc_id in location_ids if loc_id]) if location_ids else "''"}) THEN 0.9
                        ELSE 0.5
                    END as relevance_score,
                    -- Popularity normalization (simplified for SQLite)
                    (LOG(1 + p.like_count + :alpha_comment * p.comment_count) / LOG(1001)) as popularity_norm,
                    -- Recency decay (simplified for SQLite)
                    EXP(-((julianday('now') - julianday(p.created_at)) * 24 * 60) / :tau_minutes) as recency_decay
                    {distance_calc}
                FROM posts p
                LEFT JOIN locations l ON p.location_id = l.id
                WHERE ({where_clause}) {distance_filter}
            )
            SELECT 
                *,
                (:w_pop * popularity_norm + :w_recency * recency_decay) * relevance_score as combined_score
            FROM post_matches
            ORDER BY {sort_clause}
            LIMIT :limit OFFSET :offset
        """)
        
        # Prepare parameters
        weights = settings.search_weights
        
        result = await db.execute(
            search_sql,
            {
                "alpha_comment": settings.alpha_comment,
                "tau_minutes": settings.tau_minutes,
                "w_pop": weights.get("w_pop", 0.7),
                "w_recency": weights.get("w_recency", 0.3),
                "limit": limit,
                "offset": offset
            }
        )
        
        return await self._process_search_results(result, sort, has_location, db)
    
    async def _process_search_results(
        self,
        result,
        sort: str,
        has_location: bool,
        db: AsyncSession
    ) -> List[Tuple[Post, float, Optional[float]]]:
        """Process search results from either database type"""
        # Get post IDs, scores, and distances
        post_data = result.fetchall()
        if not post_data:
            return []
        
        post_ids = [str(row.id) for row in post_data]
        scores = {str(row.id): row.combined_score for row in post_data}
        distances = {str(row.id): getattr(row, 'distance_km', None) for row in post_data}
        
        # Fetch full post objects with relationships
        posts_query = select(Post).options(
            selectinload(Post.media),
            selectinload(Post.location)
        ).where(Post.id.in_(post_ids))
        
        posts_result = await db.execute(posts_query)
        posts = posts_result.scalars().all()
        
        # Combine posts with scores and distances and maintain order
        posts_with_scores = [
            (post, scores[str(post.id)], distances[str(post.id)]) 
            for post in posts
        ]
        
        # Sort according to the original sort order
        if sort == "distance" and has_location:
            posts_with_scores.sort(key=lambda x: (x[2] is None, x[2] or float('inf'), -x[1]))
        elif sort == "popularity":
            posts_with_scores.sort(key=lambda x: (-x[0].like_count - 2*x[0].comment_count, -x[1]))
        elif sort == "newest":
            posts_with_scores.sort(key=lambda x: (-x[0].created_at.timestamp(), -x[1]))
        else:  # relevance
            posts_with_scores.sort(key=lambda x: -x[1])
        
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