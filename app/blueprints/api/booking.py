from flask import Blueprint, abort, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from ...schemas.booking import CarRentalSchema, RoomBookingSchema
from ...services.booking_service import BookingService
from ...utils.response import standardized_response

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/book-room", methods=["POST"])
@jwt_required()
def book_room():
    data = request.get_json()
    try:
        validated_data = RoomBookingSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    user_id = get_jwt_identity()

    success, message = BookingService.book_room(user_id, validated_data)

    if not success:
        abort(400, description=message)

    return standardized_response(message=message, status_code=201)


@booking_bp.route("/rent-car", methods=["POST"])
@jwt_required()
def rent_car():
    data = request.get_json()
    try:
        validated_data = CarRentalSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    user_id = get_jwt_identity()

    success, message = BookingService.rent_car(user_id, validated_data)

    if not success:
        abort(400, description=message)

    return standardized_response(message=message, status_code=201)
