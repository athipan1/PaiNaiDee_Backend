import time
import logging
from flask import Blueprint, request, current_app

from ...services.search_service import SearchQuery, SearchService
from ...utils.response import standardized_response
from ...utils.text_normalization import clean_search_query, generate_search_terms
from ...models import Attraction, db
from sqlalchemy import or_, func, and_

search_bp = Blueprint("search_bp", __name__)
search_service = SearchService()

# Set up logging for search events
logger = logging.getLogger(__name__)


@search_bp.route("/search", methods=["GET", "POST"])
def search_attractions():
    """
    ค้นหาสถานที่ท่องเที่ยวด้วย fuzzy search และรองรับพารามิเตอร์หลายตัว

    Support multiple query parameters:
    - query: ข้อความค้นหา
    - language: ภาษา (th/en)
    - province: จังหวัด
    - category: หมวดหมู่
    - min_rating: คะแนนขั้นต่ำ
    - max_rating: คะแนนสูงสุด
    - sort_by: การเรียงลำดับ (relevance/rating/name)
    - limit: จำนวนผลลัพธ์ต่อหน้า
    - offset: เริ่มต้นที่ผลลัพธ์ที่
    """
    start_time = time.time()

    try:
        # รองรับทั้ง GET และ POST
        if request.method == "POST":
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()

        # สร้าง SearchQuery จากพารามิเตอร์
        search_query = SearchQuery(
            query=data.get("query", ""),
            language=data.get("language", "th"),
            province=data.get("province"),
            category=data.get("category"),
            min_rating=float(data.get("min_rating"))
            if data.get("min_rating")
            else None,
            max_rating=float(data.get("max_rating"))
            if data.get("max_rating")
            else None,
            sort_by=data.get("sort_by", "relevance"),
            limit=int(data.get("limit", 20)),
            offset=int(data.get("offset", 0)),
        )

        # ทำการค้นหา
        search_results, total_count = search_service.search_attractions_with_fuzzy(
            search_query
        )

        # แปลงผลลัพธ์เป็น dict
        results = []
        for result in search_results:
            attraction_dict = result.attraction.to_dict()
            attraction_dict.update(
                {
                    "similarity_score": result.similarity_score,
                    "matched_fields": result.matched_fields,
                    "confidence": result.similarity_score,
                }
            )
            results.append(attraction_dict)

        processing_time = round((time.time() - start_time) * 1000, 2)  # milliseconds

        response_data = {
            "results": results,
            "total_count": total_count,
            "query": search_query.query,
            "filters": {
                "language": search_query.language,
                "province": search_query.province,
                "category": search_query.category,
                "min_rating": search_query.min_rating,
                "max_rating": search_query.max_rating,
                "sort_by": search_query.sort_by,
            },
            "pagination": {
                "limit": search_query.limit,
                "offset": search_query.offset,
                "has_more": (search_query.offset + search_query.limit) < total_count,
            },
            "processing_time_ms": processing_time,
        }

        return standardized_response(data=response_data)

    except ValueError as e:
        return standardized_response(
            message=f"Invalid parameter: {e!s}", success=False, status_code=400
        )
    except Exception as e:
        return standardized_response(
            message=f"Search error: {e!s}", success=False, status_code=500
        )


@search_bp.route("/search/suggestions", methods=["GET"])
def get_search_suggestions():
    """
    ดึงข้อมูล search suggestions สำหรับ autocomplete จากฐานข้อมูลจริง
    รองรับ fuzzy search และ synonym expansion
    """
    try:
        query = request.args.get("query", "", type=str)
        language = request.args.get("language", "th", type=str)
        limit = int(request.args.get("limit", 10))

        suggestions = search_service.get_search_suggestions(query, language, limit)

        return standardized_response(data={"suggestions": suggestions})
    except Exception as e:
        return standardized_response(
            message=f"Search suggestions error: {e!s}", success=False, status_code=500
        )


@search_bp.route("/search/trending", methods=["GET"])
def get_trending_searches():
    """
    ดึงคำค้นหายอดนิยม
    """
    try:
        language = request.args.get("language", "th", type=str)
        trending = search_service.get_trending_searches(language)

        return standardized_response(data={"trending": trending})
    except Exception as e:
        return standardized_response(
            message=f"Trending search error: {e!s}", success=False, status_code=500
        )


@search_bp.route("/autocomplete", methods=["GET"])
def autocomplete():
    """
    Enhanced autocomplete endpoint with prefix matching and similarity search.
    
    Query parameters:
    - q: Search query prefix (required)
    - limit: Maximum number of suggestions (default: 10, max: 20)
    - min_length: Minimum query length to return results (default: 2)
    """
    try:
        # Check if autocomplete feature is enabled
        if not current_app.config.get('FEATURE_AUTOCOMPLETE', True):
            return standardized_response(
                message="Autocomplete feature is disabled",
                success=False,
                status_code=503
            )
        
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 20)  # Cap at 20
        min_length = int(request.args.get('min_length', 2))
        
        if not query:
            return standardized_response(
                message="Query parameter 'q' is required",
                success=False,
                status_code=400
            )
        
        if len(query) < min_length:
            return standardized_response(
                data={"suggestions": []},
                message=f"Query too short (minimum {min_length} characters)"
            )
        
        # Clean and normalize the query
        cleaned_query = clean_search_query(query, max_length=50)
        if not cleaned_query:
            return standardized_response(data={"suggestions": []})
        
        # Log search event
        logger.info(f"Autocomplete search: '{query}' -> '{cleaned_query}'")
        
        suggestions = []
        
        # Try PostgreSQL trigram search first
        try:
            # Check if we have pg_trgm support
            if "postgresql" in str(db.engine.url):
                # Use trigram similarity search
                similarity_threshold = current_app.config.get('TRIGRAM_SIM_THRESHOLD', 0.3)
                
                autocomplete_query = db.session.query(
                    Attraction.id,
                    Attraction.name,
                    Attraction.province,
                    Attraction.category,
                    func.similarity(Attraction.name, cleaned_query).label('similarity')
                ).filter(
                    func.similarity(Attraction.name, cleaned_query) > similarity_threshold
                ).order_by(
                    func.similarity(Attraction.name, cleaned_query).desc(),
                    Attraction.rating.desc().nullslast(),
                    Attraction.name
                ).limit(limit)
                
                results = autocomplete_query.all()
                
                for result in results:
                    suggestions.append({
                        "id": result.id,
                        "name": result.name,
                        "province": result.province,
                        "category": result.category,
                        "type": "attraction",
                        "similarity": round(result.similarity, 3)
                    })
        
        except Exception:
            # Fallback to ILIKE search for SQLite or if trigram fails
            pass
        
        # If no trigram results or not PostgreSQL, use ILIKE fallback
        if not suggestions:
            like_pattern = f"%{cleaned_query}%"
            prefix_pattern = f"{cleaned_query}%"
            
            # Prefix matches get higher priority
            prefix_query = db.session.query(Attraction).filter(
                or_(
                    Attraction.name.ilike(prefix_pattern),
                    Attraction.province.ilike(prefix_pattern),
                    Attraction.category.ilike(prefix_pattern)
                )
            ).order_by(
                Attraction.rating.desc().nullslast(),
                Attraction.name
            ).limit(limit // 2)
            
            # General matches
            general_query = db.session.query(Attraction).filter(
                and_(
                    or_(
                        Attraction.name.ilike(like_pattern),
                        Attraction.description.ilike(like_pattern),
                        Attraction.province.ilike(like_pattern),
                        Attraction.category.ilike(like_pattern)
                    ),
                    ~Attraction.name.ilike(prefix_pattern)  # Exclude prefix matches
                )
            ).order_by(
                Attraction.rating.desc().nullslast(),
                Attraction.name
            ).limit(limit // 2)
            
            # Combine results
            for attraction in prefix_query.all():
                suggestions.append({
                    "id": attraction.id,
                    "name": attraction.name,
                    "province": attraction.province,
                    "category": attraction.category,
                    "type": "attraction",
                    "match_type": "prefix"
                })
            
            for attraction in general_query.all():
                suggestions.append({
                    "id": attraction.id,
                    "name": attraction.name,
                    "province": attraction.province,
                    "category": attraction.category,
                    "type": "attraction",
                    "match_type": "contains"
                })
        
        # Add popular search terms if we have room
        if len(suggestions) < limit:
            remaining = limit - len(suggestions)
            search_terms = generate_search_terms(cleaned_query)
            
            if search_terms:
                # Add category suggestions
                categories = db.session.query(Attraction.category).filter(
                    Attraction.category.isnot(None),
                    or_(*[Attraction.category.ilike(f"%{term}%") for term in search_terms])
                ).distinct().limit(remaining // 2).all()
                
                for category in categories:
                    if category.category and not any(s["name"] == category.category for s in suggestions):
                        suggestions.append({
                            "name": category.category,
                            "type": "category",
                            "match_type": "category"
                        })
                
                # Add province suggestions
                provinces = db.session.query(Attraction.province).filter(
                    Attraction.province.isnot(None),
                    or_(*[Attraction.province.ilike(f"%{term}%") for term in search_terms])
                ).distinct().limit(remaining // 2).all()
                
                for province in provinces:
                    if province.province and not any(s.get("name") == province.province or s.get("province") == province.province for s in suggestions):
                        suggestions.append({
                            "name": province.province,
                            "type": "province",
                            "match_type": "location"
                        })
        
        # Limit final results
        suggestions = suggestions[:limit]
        
        return standardized_response(
            data={
                "suggestions": suggestions,
                "query": query,
                "count": len(suggestions)
            },
            message=f"Found {len(suggestions)} suggestions"
        )
        
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return standardized_response(
            message=f"Autocomplete error: {e!s}",
            success=False,
            status_code=500
        )


@search_bp.route("/locations/nearby", methods=["GET"])
def nearby_locations():
    """
    Find nearby attractions based on geographic coordinates.
    
    Query parameters:
    - lat: Latitude (required)
    - lng: Longitude (required)  
    - radius: Search radius in kilometers (default: 10, max: 50)
    - limit: Maximum number of results (default: 20)
    - category: Filter by category (optional)
    - min_rating: Minimum rating filter (optional)
    """
    try:
        # Check if nearby feature is enabled
        if not current_app.config.get('FEATURE_NEARBY', True):
            return standardized_response(
                message="Nearby locations feature is disabled",
                success=False,
                status_code=503
            )
        
        # Get parameters
        try:
            lat = float(request.args.get('lat'))
            lng = float(request.args.get('lng'))
        except (TypeError, ValueError):
            return standardized_response(
                message="Valid latitude and longitude parameters are required",
                success=False,
                status_code=400
            )
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return standardized_response(
                message="Invalid coordinates. Latitude must be -90 to 90, longitude -180 to 180",
                success=False,
                status_code=400
            )
        
        radius = min(float(request.args.get('radius', 10)), 
                    current_app.config.get('MAX_NEARBY_RADIUS_KM', 50))
        limit = min(int(request.args.get('limit', 20)), 100)
        category = request.args.get('category', '').strip()
        min_rating = request.args.get('min_rating', type=float)
        
        # Build query
        query = db.session.query(Attraction).filter(
            Attraction.latitude.isnot(None),
            Attraction.longitude.isnot(None)
        )
        
        # Apply filters
        if category:
            query = query.filter(Attraction.category.ilike(f"%{category}%"))
        
        if min_rating is not None:
            query = query.filter(Attraction.rating >= min_rating)
        
        # Get all attractions with coordinates
        attractions = query.all()
        
        # Calculate distances and filter by radius
        nearby_attractions = []
        
        for attraction in attractions:
            if attraction.latitude is None or attraction.longitude is None:
                continue
                
            # Calculate distance using Haversine formula (simplified)
            import math
            
            lat1, lon1 = math.radians(lat), math.radians(lng)
            lat2, lon2 = math.radians(attraction.latitude), math.radians(attraction.longitude)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = (math.sin(dlat/2)**2 + 
                 math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
            c = 2 * math.asin(math.sqrt(a))
            distance = 6371 * c  # Earth's radius in km
            
            if distance <= radius:
                nearby_attractions.append({
                    "id": attraction.id,
                    "name": attraction.name,
                    "description": attraction.description,
                    "province": attraction.province,
                    "category": attraction.category,
                    "rating": attraction.rating,
                    "latitude": attraction.latitude,
                    "longitude": attraction.longitude,
                    "distance_km": round(distance, 2),
                    "image_url": attraction.image_url,
                    "contact_phone": attraction.contact_phone,
                    "website": attraction.website
                })
        
        # Sort by distance
        nearby_attractions.sort(key=lambda x: x["distance_km"])
        
        # Limit results
        nearby_attractions = nearby_attractions[:limit]
        
        # Log search event
        logger.info(f"Nearby search: lat={lat}, lng={lng}, radius={radius}km, found={len(nearby_attractions)}")
        
        return standardized_response(
            data={
                "locations": nearby_attractions,
                "search_center": {"latitude": lat, "longitude": lng},
                "radius_km": radius,
                "total_found": len(nearby_attractions),
                "filters": {
                    "category": category if category else None,
                    "min_rating": min_rating
                }
            },
            message=f"Found {len(nearby_attractions)} locations within {radius}km"
        )
        
    except Exception as e:
        logger.error(f"Nearby locations error: {e}")
        return standardized_response(
            message=f"Nearby locations error: {e!s}",
            success=False,
            status_code=500
        )
