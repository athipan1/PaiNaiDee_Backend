from flask import Blueprint, request
from src.models import db, Attraction
from src.utils.response import standardized_response
from src.services.search_service import SearchService, SearchQuery
import time

search_bp = Blueprint("search_bp", __name__)
search_service = SearchService()


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
            min_rating=float(data.get("min_rating")) if data.get("min_rating") else None,
            max_rating=float(data.get("max_rating")) if data.get("max_rating") else None,
            sort_by=data.get("sort_by", "relevance"),
            limit=int(data.get("limit", 20)),
            offset=int(data.get("offset", 0))
        )
        
        # ทำการค้นหา
        search_results, total_count = search_service.search_attractions_with_fuzzy(search_query)
        
        # แปลงผลลัพธ์เป็น dict
        results = []
        for result in search_results:
            attraction_dict = result.attraction.to_dict()
            attraction_dict.update({
                "similarity_score": result.similarity_score,
                "matched_fields": result.matched_fields,
                "confidence": result.similarity_score
            })
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
                "sort_by": search_query.sort_by
            },
            "pagination": {
                "limit": search_query.limit,
                "offset": search_query.offset,
                "has_more": (search_query.offset + search_query.limit) < total_count
            },
            "processing_time_ms": processing_time
        }
        
        return standardized_response(data=response_data)
    
    except ValueError as e:
        return standardized_response(
            message=f"Invalid parameter: {str(e)}", 
            success=False, 
            status_code=400
        )
    except Exception as e:
        return standardized_response(
            message=f"Search error: {str(e)}", 
            success=False, 
            status_code=500
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
            message=f"Search suggestions error: {str(e)}", 
            success=False, 
            status_code=500
        )


@search_bp.route("/search/filters", methods=["GET"])
def get_search_filters():
    """Return available filters for attractions."""
    try:
        filters = search_service.get_available_filters()
        return standardized_response(data=filters)
    except Exception as e:
        return standardized_response(
            message=f"Error retrieving filters: {str(e)}",
            success=False,
            status_code=500
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
            message=f"Trending search error: {str(e)}", 
            success=False, 
            status_code=500
        )
