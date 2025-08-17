from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.review_service import ReviewService
from src.utils.response import standardized_response
from src.schemas.review import ReviewSchema
from marshmallow import ValidationError

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/reviews", methods=["POST"])
@jwt_required()
def add_review():
    data = request.get_json()
    try:
        validated_data = ReviewSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    current_user_id = get_jwt_identity()

    review, message = ReviewService.add_review(current_user_id, validated_data)

    if not review:
        abort(400, description=message)

    return standardized_response(
        message=message, status_code=201
    )


@reviews_bp.route("/attractions/<int:attraction_id>/reviews", methods=["GET"])
def get_attraction_reviews(attraction_id):
    """Get all reviews for a specific attraction."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        reviews_data = ReviewService.get_reviews_by_attraction(attraction_id, page, limit)
        return standardized_response(
            data=reviews_data,
            message="Reviews retrieved successfully."
        )
    except Exception as e:
        abort(500, description=f"Failed to retrieve reviews. Error: {e}")


@reviews_bp.route("/reviews/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review(review_id):
    """Update a review by its ID (only by the review author)."""
    data = request.get_json()
    try:
        validated_data = ReviewSchema(partial=True).load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    current_user_id = get_jwt_identity()

    review, message = ReviewService.update_review(review_id, current_user_id, validated_data)
    if not review:
        abort(403, description=message)

    return standardized_response(
        data=review.to_dict(),
        message=message
    )


@reviews_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):
    """Delete a review by its ID (only by the review author)."""
    current_user_id = get_jwt_identity()

    success, message = ReviewService.delete_review(review_id, current_user_id)
    if not success:
        abort(403, description=message)

    return standardized_response(message=message)
