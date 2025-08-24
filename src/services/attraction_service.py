from src.models import db, Attraction
from werkzeug.utils import secure_filename
import os
import math


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
        attraction = db.session.get(Attraction, attraction_id)
        if not attraction:
            from flask import abort
            abort(404, description="Attraction not found.")
        return attraction

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
        attraction = db.session.get(Attraction, attraction_id)
        if not attraction:
            from flask import abort
            abort(404, description="Attraction not found.")
        for key, value in data.items():
            if hasattr(attraction, key):
                setattr(attraction, key, value)
        db.session.commit()
        return attraction

    @staticmethod
    def delete_attraction(attraction_id):
        attraction = db.session.get(Attraction, attraction_id)
        if not attraction:
            from flask import abort
            abort(404, description="Attraction not found.")
        db.session.delete(attraction)
        db.session.commit()

    @staticmethod
    def get_attractions_by_category(category_name):
        """Get attractions by category name using case-insensitive search"""
        query = Attraction.query.filter(
            Attraction.category.ilike(f"%{category_name}%")
        )
        attractions = query.order_by(Attraction.name).all()
        return attractions

    @staticmethod
    def get_nearby_attractions(attraction_id, radius_km=10):
        """Find nearby attractions using the Haversine formula."""
        base_attraction = AttractionService.get_attraction_by_id(attraction_id)
        if not base_attraction.latitude or not base_attraction.longitude:
            return []

        R = 6371  # Earth radius in kilometers
        base_lat = math.radians(base_attraction.latitude)
        base_lon = math.radians(base_attraction.longitude)

        nearby_attractions = []
        all_attractions = Attraction.query.filter(Attraction.id != attraction_id).all()

        for attraction in all_attractions:
            if attraction.latitude and attraction.longitude:
                lat = math.radians(attraction.latitude)
                lon = math.radians(attraction.longitude)

                dlon = lon - base_lon
                dlat = lat - base_lat

                a = (
                    math.sin(dlat / 2) ** 2
                    + math.cos(base_lat) * math.cos(lat) * math.sin(dlon / 2) ** 2
                )
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                distance = R * c

                if distance <= radius_km:
                    nearby_attractions.append(attraction)

        return nearby_attractions
