from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from src.services.attraction_service import AttractionService
from src.services.place_detail_service import PlaceDetailService
from src.utils.response import standardized_response
from src.schemas.place_detail import PlaceDetailSchema
from marshmallow import ValidationError

places_bp = Blueprint("places", __name__)


@places_bp.route("/places/<int:place_id>", methods=["GET"])
def get_place_detail(place_id):
    """Get place details - same as attraction detail but with place_detail info"""
    attraction = AttractionService.get_attraction_by_id(place_id)
    return standardized_response(
        data=attraction.to_dict(),
        message="Place retrieved successfully.",
    )


@places_bp.route("/places/<int:place_id>/details", methods=["POST"])
@jwt_required()
def add_place_details(place_id):
    """Add additional details for a place"""
    data = request.get_json()
    
    try:
        validated_data = PlaceDetailSchema().load(data)
    except ValidationError as err:
        return standardized_response(
            data=err.messages, success=False, status_code=400
        )
    
    try:
        place_detail = PlaceDetailService.add_place_detail(place_id, validated_data)
        return standardized_response(
            data=place_detail.to_dict(),
            message="Place details added successfully.",
            status_code=201,
        )
    except Exception as e:
        return standardized_response(
            message=str(e), success=False, status_code=400
        )


@places_bp.route("/places/<int:place_id>/details", methods=["PUT"])
@jwt_required()
def update_place_details(place_id):
    """Update additional details for a place"""
    data = request.get_json()
    
    try:
        validated_data = PlaceDetailSchema().load(data)
    except ValidationError as err:
        return standardized_response(
            data=err.messages, success=False, status_code=400
        )
    
    try:
        place_detail = PlaceDetailService.update_place_detail(place_id, validated_data)
        return standardized_response(
            data=place_detail.to_dict(),
            message="Place details updated successfully.",
        )
    except Exception as e:
        return standardized_response(
            message=str(e), success=False, status_code=400
        )


@places_bp.route("/places/<int:place_id>/details", methods=["DELETE"])
@jwt_required()
def delete_place_details(place_id):
    """Delete additional details for a place"""
    try:
        PlaceDetailService.delete_place_detail(place_id)
        return standardized_response(
            message="Place details deleted successfully."
        )
    except Exception as e:
        return standardized_response(
            message=str(e), success=False, status_code=400
        )