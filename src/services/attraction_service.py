from src.models import db, Attraction, Review
from sqlalchemy import func
from sqlalchemy.orm import joinedload


class AttractionService:
    @staticmethod
    def get_all_attractions(page, limit, q, province):
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
        query = db.session.query(
            Attraction,
            review_stats_subquery.c.average_rating,
            review_stats_subquery.c.total_reviews,
        ).outerjoin(
            review_stats_subquery,
            Attraction.id == review_stats_subquery.c.place_id,
        )

        # Apply search and filter criteria to the main query.
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
            .filter(Attraction.id == attraction_id)
            .first()
        )

        if not result:
            from flask import abort

            # Check if the attraction exists at all, even without reviews
            attraction_exists = (
                db.session.query(Attraction.id).filter_by(id=attraction_id).first()
            )
            if not attraction_exists:
                abort(404, description="Attraction not found.")

            # If it exists but has no reviews, return the object with None for stats
            attraction = db.session.get(Attraction, attraction_id)
            return attraction, None, None

        # The query returns a tuple (Attraction, average_rating, total_reviews)
        return result

    @staticmethod
    def add_attraction(data):
        new_attraction = Attraction(
            name=data.get("name"),
            description=data.get("description"),
            location=data.get("location"),
            province=data.get("province"),
            district=data.get("district"),
            address=data.get("address"),
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
