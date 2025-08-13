from src.models import db, Review, User, Attraction
from sqlalchemy import func


class ReviewService:
    @staticmethod
    def add_review(user_id, data):
        user = db.session.get(User, user_id)
        if not user:
            return None, "User not found."

        # Check if attraction exists
        attraction = db.session.get(Attraction, data["place_id"])
        if not attraction:
            return None, "Attraction not found."

        # Check if user has already reviewed this attraction
        existing_review = Review.query.filter_by(
            user_id=user_id, 
            place_id=data["place_id"]
        ).first()
        if existing_review:
            return None, "You have already reviewed this attraction."

        new_review = Review(
            place_id=data["place_id"],
            user_id=user_id,
            rating=data["rating"],
            comment=data.get("comment"),
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review, "Review added successfully."

    @staticmethod
    def get_reviews_by_attraction(attraction_id, page=1, limit=10):
        """Get paginated reviews for a specific attraction with average rating."""
        # Check if attraction exists
        attraction = db.session.get(Attraction, attraction_id)
        if not attraction:
            raise ValueError("Attraction not found.")

        # Get average rating
        avg_rating_query = db.session.query(
            func.avg(Review.rating).label('average_rating'),
            func.count(Review.id).label('total_reviews')
        ).filter(Review.place_id == attraction_id).first()

        avg_rating = float(avg_rating_query.average_rating) if avg_rating_query.average_rating else 0
        total_reviews = avg_rating_query.total_reviews or 0

        # Get paginated reviews
        paginated_reviews = Review.query.filter_by(place_id=attraction_id)\
            .order_by(Review.created_at.desc())\
            .paginate(page=page, per_page=limit, error_out=False)

        reviews_data = [review.to_dict() for review in paginated_reviews.items]

        return {
            "reviews": reviews_data,
            "average_rating": round(avg_rating, 1),
            "total_reviews": total_reviews,
            "pagination": {
                "current_page": paginated_reviews.page,
                "total_pages": paginated_reviews.pages,
                "total_items": paginated_reviews.total,
                "has_next": paginated_reviews.has_next,
                "has_prev": paginated_reviews.has_prev,
            }
        }

    @staticmethod
    def update_review(review_id, user_id, data):
        """Update a review if it belongs to the user."""
        review = db.session.get(Review, review_id)
        if not review:
            return None, "Review not found."

        if review.user_id != int(user_id):
            return None, "You can only edit your own reviews."

        # Update fields if provided
        if "rating" in data:
            review.rating = data["rating"]
        if "comment" in data:
            review.comment = data["comment"]

        db.session.commit()
        return review, "Review updated successfully."

    @staticmethod
    def delete_review(review_id, user_id):
        """Delete a review if it belongs to the user."""
        review = db.session.get(Review, review_id)
        if not review:
            return False, "Review not found."

        if review.user_id != int(user_id):
            return False, "You can only delete your own reviews."

        db.session.delete(review)
        db.session.commit()
        return True, "Review deleted successfully."
