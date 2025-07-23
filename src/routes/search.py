from flask import Blueprint, request
from src.models import db, Attraction
from src.utils.response import standardized_response

search_bp = Blueprint("search_bp", __name__)


@search_bp.route("/search/suggestions", methods=["GET"])
def get_search_suggestions():
    """
    ดึงข้อมูล search suggestions สำหรับ autocomplete จากฐานข้อมูลจริง
    """
    query = request.args.get("query", "", type=str)
    suggestions = []

    if query:
        # ค้นหา Attractions ตาม name, province, category
        attractions = (
            db.session.query(Attraction)
            .filter(
                (Attraction.name.ilike(f"%{query}%"))
                | (Attraction.province.ilike(f"%{query}%"))
                | (Attraction.category.ilike(f"%{query}%"))
            )
            .limit(10)
            .all()
        )
        
        for attraction in attractions:
            suggestions.append(
                {
                    "id": f"attraction-{attraction.id}",
                    "type": "attraction",
                    "text": attraction.name,
                    "description": f"{attraction.province}, {attraction.category}",
                    "province": attraction.province,
                    "category": attraction.category,
                    "confidence": 1.0,
                    "image": attraction.main_image_url,
                }
            )

    return standardized_response(data={"suggestions": suggestions[:10]})
