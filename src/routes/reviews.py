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
