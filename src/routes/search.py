from flask import Blueprint, request
from src.models import db, Place, Province, Category, Tag  # ฟังก์ชันและโมเดลจากฐานข้อมูลจริง
from src.utils import standardized_response

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """
    ดึงข้อมูล search suggestions สำหรับ autocomplete จากฐานข้อมูลจริง
    """
    query = request.args.get('query', '', type=str)
    language = request.args.get('language', 'th', type=str)
    suggestions = []

    if query:
        # 1. ค้นหา Place
        places = (
            db.session.query(Place)
            .filter(
                (Place.name.ilike(f"%{query}%")) |
                (Place.name_local.ilike(f"%{query}%"))
            )
            .limit(5)
            .all()
        )
        for place in places:
            name_to_show = place.name_local if language == "th" and place.name_local else place.name
            suggestions.append({
                "id": f"place-{place.id}",
                "type": "place",
                "text": name_to_show,
                "description": place.province_local if language == "th" else place.province,
                "province": place.province_local if language == "th" else place.province,
                "category": place.category,
                "confidence": 1.0,
                "image": getattr(place, "image", None)
            })

        # 2. ค้นหา Province
        provinces = (
            db.session.query(Province)
            .filter(
                (Province.name.ilike(f"%{query}%")) |
                (Province.name_local.ilike(f"%{query}%"))
            )
            .limit(5)
            .all()
        )
        for province in provinces:
            name_to_show = province.name_local if language == "th" and province.name_local else province.name
            suggestions.append({
                "id": f"province-{province.id}",
                "type": "province",
                "text": name_to_show,
                "description": "จังหวัด" if language == "th" else "Province",
                "confidence": 1.0
            })

        # 3. ค้นหา Category
        categories = (
            db.session.query(Category)
            .filter(
                (Category.name.ilike(f"%{query}%")) |
                (Category.name_local.ilike(f"%{query}%"))
            )
            .limit(5)
            .all()
        )
        for category in categories:
            name_to_show = category.name_local if language == "th" and category.name_local else category.name
            suggestions.append({
                "id": f"category-{category.id}",
                "type": "category",
                "text": name_to_show,
                "description": "หมวดหมู่" if language == "th" else "Category",
                "confidence": 1.0
            })

        # 4. ค้นหา Tag (Option)
        tags = (
            db.session.query(Tag)
            .filter(
                (Tag.name.ilike(f"%{query}%")) |
                (Tag.name_local.ilike(f"%{query}%"))
            )
            .limit(5)
            .all()
        )
        for tag in tags:
            name_to_show = tag.name_local if language == "th" and tag.name_local else tag.name
            suggestions.append({
                "id": f"tag-{tag.id}",
                "type": "tag",
                "text": name_to_show,
                "description": "แท็ก" if language == "th" else "Tag",
                "confidence": 1.0
            })

    # ตัด suggestions ให้เหลือสูงสุด 10 รายการ
    return standardized_response(data={"suggestions": suggestions[:10]})