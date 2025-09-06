import traceback
from flask import Blueprint, request, abort, current_app
from flask_jwt_extended import jwt_required
from src.services.attraction_service import AttractionService
from src.utils.response import standardized_response
from src.schemas.attraction import AttractionSchema
from marshmallow import ValidationError

attractions_bp = Blueprint("attractions", __name__)


@attractions_bp.route("/attractions", methods=["GET"])
def get_all_attractions():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)
        q = request.args.get("q")
        province = request.args.get("province")
        category = request.args.get("category")

        paginated_results = AttractionService.get_all_attractions(
            page, limit, q, province, category
        )

        # The service now returns tuples of (Attraction, avg_rating, total_reviews).
        # We unpack these and pass the stats to the to_dict method.
        results = [
            attraction.to_dict(average_rating=avg_rating, total_reviews=total_rev)
            for attraction, avg_rating, total_rev in paginated_results.items
        ]

        pagination_data = {
            "total_pages": paginated_results.pages,
            "current_page": paginated_results.page,
            "total_items": paginated_results.total,
            "has_next": paginated_results.has_next,
            "has_prev": paginated_results.has_prev,
        }

        return standardized_response(
            data={"attractions": results, "pagination": pagination_data},
            message="Attractions retrieved successfully.",
        )
    except Exception:
        current_app.logger.error(traceback.format_exc())
        return standardized_response(
            message="An unexpected error occurred.", success=False, status_code=500
        )


@attractions_bp.route("/attractions/<int:attraction_id>", methods=["GET"])
def get_attraction_detail(attraction_id):
    # The service now returns a tuple: (Attraction, avg_rating, total_reviews)
    result = AttractionService.get_attraction_by_id(attraction_id)
    if not result:
        abort(404, description="Attraction not found.")

    attraction, avg_rating, total_reviews = result

    return standardized_response(
        data=attraction.to_dict(
            average_rating=avg_rating, total_reviews=total_reviews
        ),
        message="Attraction retrieved successfully.",
    )


@attractions_bp.route("/attractions", methods=["POST"])
@jwt_required()
def add_attraction():
    file = request.files.get("cover_image")

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    try:
        # We can use partial validation here if some fields are truly optional
        # For now, stick to the schema's definition of required fields.
        validated_data = AttractionSchema().load(data)
    except ValidationError as err:
        return standardized_response(
            data=err.messages, success=False, status_code=400
        )

    try:
        # The service layer already handles the file being None
        new_attraction = AttractionService.add_attraction(validated_data, file)
        return standardized_response(
            data=new_attraction.to_dict(),
            message="Attraction added successfully.",
            status_code=201,
        )
    except Exception as e:
        current_app.logger.error(f"Error adding attraction: {e}\n{traceback.format_exc()}")
        abort(500, description=f"Failed to add attraction. Error: {e}")


@attractions_bp.route("/attractions/<int:attraction_id>", methods=["PUT"])
@jwt_required()
def update_attraction(attraction_id):
    data = request.get_json()
    try:
        validated_data = AttractionSchema(partial=True).load(data)
    except ValidationError as err:
        return standardized_response(
            data=err.messages, success=False, status_code=400
        )

    try:
        attraction = AttractionService.update_attraction(
            attraction_id, validated_data
        )
        return standardized_response(
            data=attraction.to_dict(),
            message="Attraction updated successfully.",
        )
    except Exception as e:
        abort(500, description=f"Failed to update attraction. Error: {e}")


@attractions_bp.route("/attractions/<int:attraction_id>", methods=["DELETE"])
@jwt_required()
def delete_attraction(attraction_id):
    try:
        AttractionService.delete_attraction(attraction_id)
        return standardized_response(
            message="Attraction deleted successfully."
        )
    except Exception as e:
        abort(500, description=f"Failed to delete attraction. Error: {e}")


@attractions_bp.route("/attractions/category/<category_name>", methods=["GET"])
def get_attractions_by_category(category_name):
    """Get attractions by category name - public access, no authentication required"""
    try:
        attractions = AttractionService.get_attractions_by_category(category_name)
        results = [attraction.to_category_dict() for attraction in attractions]
        
        return standardized_response(
            data=results,
            message=f"Attractions in category '{category_name}' retrieved successfully.",
        )
    except Exception as e:
        abort(500, description=f"Failed to retrieve attractions by category. Error: {e}")


@attractions_bp.route("/accommodations/nearby/<int:attraction_id>", methods=["GET"])
def get_nearby_accommodations(attraction_id):
    """Get nearby accommodations for a given attraction"""
    radius = request.args.get("radius", 10, type=int)
    try:
        nearby_accommodations = AttractionService.get_nearby_attractions(
            attraction_id, radius_km=radius
        )
        results = [
            accommodation.to_dict() for accommodation in nearby_accommodations
        ]
        return standardized_response(
            data=results,
            message="Nearby accommodations retrieved successfully.",
        )
    except Exception as e:
        abort(500, description=f"Failed to retrieve nearby accommodations. Error: {e}")
