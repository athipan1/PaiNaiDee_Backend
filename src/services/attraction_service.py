from src.models import db, Attraction
from werkzeug.utils import secure_filename
import os


class AttractionService:
    @staticmethod
    def get_all_attractions(page, limit, q, province, category):
        query = Attraction.query

        if q:
            search_term = f"%{q}%"
            query = query.filter(
                db.or_(
                    Attraction.name.ilike(search_term),
                    Attraction.description.ilike(search_term),
                )
            )
        if province:
            query = query.filter(Attraction.province.ilike(f"%{province}%"))
        if category:
            query = query.filter(Attraction.category.ilike(f"%{category}%"))

        paginated_attractions = query.order_by(Attraction.name).paginate(
            page=page, per_page=limit, error_out=False
        )
        return paginated_attractions

    @staticmethod
    def get_attraction_by_id(attraction_id):
        return Attraction.query.get_or_404(
            attraction_id, description="Attraction not found."
        )

    @staticmethod
    def add_attraction(data, file):
        filename = secure_filename(file.filename)
        upload_path = os.path.join("uploads", filename)
        file.save(upload_path)

        new_attraction = Attraction(
            name=data.get("name"),
            description=data.get("description"),
            address=data.get("address"),
            province=data.get("province"),
            district=data.get("district"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            category=data.get("category"),
            opening_hours=data.get("opening_hours"),
            entrance_fee=data.get("entrance_fee"),
            contact_phone=data.get("contact_phone"),
            website=data.get("website"),
            main_image_url=filename,
            image_urls=data.get("image_urls"),
        )
        db.session.add(new_attraction)
        db.session.commit()
        return new_attraction

    @staticmethod
    def update_attraction(attraction_id, data):
        attraction = Attraction.query.get_or_404(
            attraction_id, description="Attraction not found."
        )
        for key, value in data.items():
            if hasattr(attraction, key):
                setattr(attraction, key, value)
        db.session.commit()
        return attraction

    @staticmethod
    def delete_attraction(attraction_id):
        attraction = Attraction.query.get_or_404(
            attraction_id, description="Attraction not found."
        )
        db.session.delete(attraction)
        db.session.commit()
