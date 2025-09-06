from src.models import db, Attraction, Review
from werkzeug.utils import secure_filename
import os
import math
from sqlalchemy import func
from sqlalchemy.orm import joinedload


class AttractionService:
    @staticmethod
    def get_all_attractions(page, limit, q, province, category):
        """
        Retrieves attractions with their review statistics in a single, optimized query.
        This approach uses a subquery to pre-calculate review stats and joins it
        with the attractions table, avoiding the N+1 query problem.
        """
        # Create a subquery to calculate the average rating and total number of reviews for each attraction.
        review_stats_subquery = (
            db.session.query(
                Review.place_id,
                func.avg(Review.rating).label("average_rating"),
                func.count(Review.id).label("total_reviews"),
            )
            .group_by(Review.place_id)
            .subquery()
        )

        # Main query to select attractions and join them with the review statistics subquery.
        # An outerjoin (LEFT JOIN) is used to ensure all attractions are returned, even those without reviews.
        query = (
            db.session.query(
                Attraction,
                review_stats_subquery.c.average_rating,
                review_stats_subquery.c.total_reviews,
            )
            .outerjoin(
                review_stats_subquery,
                Attraction.id == review_stats_subquery.c.place_id,
            )
            .options(
                joinedload(Attraction.rooms),
                joinedload(Attraction.cars),
            )
        )

        # Apply search and filter criteria to the main query.
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                db.or_(
                    func.lower(Attraction.name).like(func.lower(search_term)),
                    func.lower(Attraction.description).like(func.lower(search_term)),
                )
            )
        if province:
            query = query.filter(func.lower(Attraction.province).like(func.lower(f"%{province}%")))
        if category:
            query = query.filter(func.lower(Attraction.category).like(func.lower(f"%{category}%")))

        # Order the results and apply pagination.
        paginated_results = query.order_by(Attraction.name).paginate(
            page=page, per_page=limit, error_out=False
        )

        return paginated_results

    @staticmethod
    def get_attraction_by_id(attraction_id):
        """
        Retrieves a single attraction by its ID, along with its review statistics,
        using an optimized query to prevent the N+1 problem.
        """
        # Subquery to calculate review statistics for the specific attraction
        review_stats_subquery = (
            db.session.query(
                Review.place_id,
                func.avg(Review.rating).label("average_rating"),
                func.count(Review.id).label("total_reviews"),
            )
            .filter(Review.place_id == attraction_id)
            .group_by(Review.place_id)
            .subquery()
        )

        # Main query to get the attraction and join with its review stats
        result = (
            db.session.query(
                Attraction,
                review_stats_subquery.c.average_rating,
                review_stats_subquery.c.total_reviews,
            )
            .outerjoin(
                review_stats_subquery,
                Attraction.id == review_stats_subquery.c.place_id,
            )
            .options(
                joinedload(Attraction.rooms),
                joinedload(Attraction.cars),
            )
            .filter(Attraction.id == attraction_id)
            .first()
        )

        if not result:
            from flask import abort

            # Check if the attraction exists at all, even without reviews
            attraction_exists = db.session.query(Attraction.id).filter_by(id=attraction_id).first()
            if not attraction_exists:
                abort(404, description="Attraction not found.")

            # If it exists but has no reviews, return the object with None for stats
            attraction = db.session.get(Attraction, attraction_id)
            return attraction, None, None


        # The query returns a tuple (Attraction, average_rating, total_reviews)
        return result

    @staticmethod
    def add_attraction(data, file):
        image_url = "https://example.com/default.jpg"
        if file:
            filename = secure_filename(file.filename)
            upload_path = os.path.join("uploads", filename)
            file.save(upload_path)
            image_url = filename

        new_attraction = Attraction(
            name=data.get("name"),
            description=data.get("description"),
            province=data.get("province"),
            district=data.get("district"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            category=data.get("category"),
            opening_hours=data.get("opening_hours"),
            entrance_fee=data.get("entrance_fee"),
            contact_phone=data.get("contact_phone"),
            website=data.get("website"),
            main_image_url=image_url,
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
