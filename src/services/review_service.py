from src.models import db, Review, User


class ReviewService:
    @staticmethod
    def add_review(user_id, data):
        user = User.query.get(user_id)
        if not user:
            return None, "User not found."

        new_review = Review(
            place_id=data["place_id"],
            user_name=user.username,
            rating=data["rating"],
            comment=data.get("comment"),
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review, "Review added successfully."
