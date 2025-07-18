from flask import Blueprint, jsonify, request, make_response
from src.models import db, Review

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    if not data:
        return make_response(jsonify(message="Invalid data"), 400)

    # Validate rating
    rating = data.get('rating')
    if rating is None or not (1 <= rating <= 5):
        return make_response(jsonify(message="Rating must be between 1 and 5"), 400)

    # Validate comment length
    comment = data.get('comment')
    if comment and len(comment) > 500:
        return make_response(jsonify(message="Comment must not exceed 500 characters"), 400)

    try:
        new_review = Review(
            place_id=data.get('place_id'),
            user_name=data.get('user_name'),
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()
        response = make_response(jsonify(message="รีวิวถูกบันทึกแล้ว"), 201)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        response = make_response(jsonify(error="Insert failed"), 500)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
