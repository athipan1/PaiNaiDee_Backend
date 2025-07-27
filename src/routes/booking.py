from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.booking_service import BookingService
from src.utils.response import standardized_response
from src.schemas.booking import RoomBookingSchema, CarRentalSchema
from marshmallow import ValidationError

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/book-room", methods=["POST"])
@jwt_required()
def book_room():
    """
    Book a room for specific dates
    ---
    tags:
      - Booking
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - room_id
            - date_start
            - date_end
          properties:
            room_id:
              type: integer
              description: ID of the room to book
            date_start:
              type: string
              format: date
              description: Start date of booking (YYYY-MM-DD)
            date_end:
              type: string
              format: date
              description: End date of booking (YYYY-MM-DD)
    responses:
      201:
        description: Room booked successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Invalid booking data or room not available
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
      401:
        description: Authentication required
    """
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
