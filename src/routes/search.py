from flask import Blueprint, request
from src.models import db, Attraction
from src.utils.response import standardized_response

search_bp = Blueprint("search_bp", __name__)


@search_bp.route("/search/suggestions", methods=["GET"])
def get_search_suggestions():
    """
    ดึงข้อมูล search suggestions สำหรับ autocomplete จากฐานข้อมูลจริง
    """
    try:
        query = request.args.get("query", "", type=str)
        language = request.args.get("language", "th", type=str)
        suggestions = []

        if query:
            # ค้นหา Attractions
            attractions = (
                db.session.query(Attraction)
                .filter(
                    (Attraction.name.ilike(f"%{query}%"))
                )
                .limit(5)
                .all()
            )
            for attraction in attractions:
                suggestions.append(
                    {
                        "id": f"attraction-{attraction.id}",
                        "type": "attraction",
                        "text": attraction.name,
                        "description": attraction.province,
                        "province": attraction.province,
                        "category": attraction.category,
                        "confidence": 1.0,
                        "image": attraction.main_image_url,
                    }
                )

            # ค้นหา Provinces (จาก attractions ที่มีอยู่)
            provinces = (
                db.session.query(Attraction.province)
                .filter(Attraction.province.ilike(f"%{query}%"))
                .distinct()
                .limit(5)
                .all()
            )
            for province_tuple in provinces:
                province = province_tuple[0]
                if province:
                    suggestions.append(
                        {
                            "id": f"province-{province.lower().replace(' ', '-')}",
                            "type": "province",
                            "text": province,
                            "description": "จังหวัด" if language == "th" else "Province",
                            "confidence": 1.0,
                        }
                    )

            # ค้นหา Categories (จาก attractions ที่มีอยู่)
            categories = (
                db.session.query(Attraction.category)
                .filter(Attraction.category.ilike(f"%{query}%"))
                .distinct()
                .limit(5)
                .all()
            )
            for category_tuple in categories:
                category = category_tuple[0]
                if category:
                    suggestions.append(
                        {
                            "id": f"category-{category.lower().replace(' ', '-')}",
                            "type": "category",
                            "text": category,
                            "description": "หมวดหมู่" if language == "th" else "Category",
                            "confidence": 1.0,
                        }
                    )

        # ตัด suggestions ให้เหลือสูงสุด 10 รายการ
        return standardized_response(data={"suggestions": suggestions[:10]})
    except Exception as e:
        return standardized_response(message=f"Search error: {str(e)}", success=False, status_code=500)
