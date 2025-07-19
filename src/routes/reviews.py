from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Review, User
from src.utils import standardized_response

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews', methods=['POST'])
@jwt_required()
def add_review():
    data = request.get_json()
    print("Request json data:", data)
    if not data:
        abort(400, description="Invalid data.")

    rating = data.get('rating')
    if rating is None or not (1 <= rating <= 5):
        abort(400, description="Rating must be between 1 and 5.")

    comment = data.get('comment')
    if comment and len(comment) > 500:
        abort(400, description="Comment must not exceed 500 characters.")

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    try:
        new_review = Review(
            place_id=data.get('place_id'),
            user_name=user.username,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()
        return standardized_response(message="Review added successfully.", status_code=201)
    except Exception:
        db.session.rollback()
        abort(500, description="Failed to add review.")
