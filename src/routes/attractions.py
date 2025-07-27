from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required
from src.services.attraction_service import AttractionService
from src.utils.response import standardized_response
from src.schemas.attraction import AttractionSchema
from marshmallow import ValidationError

attractions_bp = Blueprint("attractions", __name__)


@attractions_bp.route("/attractions", methods=["GET"])
def get_all_attractions():
    """
    Get all attractions with filtering and pagination
    ---
    tags:
      - Attractions
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number for pagination
      - name: limit
        in: query
        type: integer
        default: 10
        description: Number of items per page
      - name: q
        in: query
        type: string
        description: Search term for attraction name or description
      - name: province
        in: query
        type: string
        description: Filter by province
      - name: category
        in: query
        type: string
        description: Filter by category
    responses:
      200:
        description: List of attractions retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                attractions:
                  type: array
                  items:
                    type: object
                pagination:
                  type: object
                  properties:
                    total_pages:
                      type: integer
                    current_page:
                      type: integer
                    total_items:
                      type: integer
                    has_next:
                      type: boolean
                    has_prev:
                      type: boolean
    """
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    q = request.args.get("q")
    province = request.args.get("province")
    category = request.args.get("category")

    paginated_attractions = AttractionService.get_all_attractions(
        page, limit, q, province, category
    )
    results = [attraction.to_dict() for attraction in paginated_attractions.items]

    pagination_data = {
        "total_pages": paginated_attractions.pages,
        "current_page": paginated_attractions.page,
        "total_items": paginated_attractions.total,
        "has_next": paginated_attractions.has_next,
        "has_prev": paginated_attractions.has_prev,
    }

    return standardized_response(
        data={"attractions": results, "pagination": pagination_data},
        message="Attractions retrieved successfully.",
    )


@attractions_bp.route("/attractions/<int:attraction_id>", methods=["GET"])
def get_attraction_detail(attraction_id):
    """
    Get detailed information about a specific attraction
    ---
    tags:
      - Attractions
    parameters:
      - name: attraction_id
        in: path
        type: integer
        required: true
        description: ID of the attraction to retrieve
    responses:
      200:
        description: Attraction details retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                description:
                  type: string
                address:
                  type: string
                province:
                  type: string
                district:
                  type: string
                location:
                  type: object
                  properties:
                    lat:
                      type: number
                    lng:
                      type: number
                category:
                  type: string
                opening_hours:
                  type: string
                entrance_fee:
                  type: string
                contact_phone:
                  type: string
                website:
                  type: string
                images:
                  type: array
                  items:
                    type: string
                rooms:
                  type: array
                  items:
                    type: object
                cars:
                  type: array
                  items:
                    type: object
                average_rating:
                  type: number
                total_reviews:
                  type: integer
      404:
        description: Attraction not found
    """
    attraction = AttractionService.get_attraction_by_id(attraction_id)
    return standardized_response(
        data=attraction.to_dict(),
        message="Attraction retrieved successfully.",
    )


@attractions_bp.route("/attractions", methods=["POST"])
@jwt_required()
def add_attraction():
    if "cover_image" not in request.files:
        abort(400, description="Missing 'cover_image' in request.")

    file = request.files["cover_image"]
    if file.filename == "":
        abort(400, description="No selected file.")

    data = request.form.to_dict()
    try:
        validated_data = AttractionSchema().load(data)
    except ValidationError as err:
        return standardized_response(
            data=err.messages, success=False, status_code=400
        )

    try:
        new_attraction = AttractionService.add_attraction(validated_data, file)
        return standardized_response(
            data={"id": new_attraction.id},
            message="Attraction added successfully.",
            status_code=201,
        )
    except Exception as e:
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
