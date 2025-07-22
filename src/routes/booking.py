from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Room, Car
from src.utils import standardized_response

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book-room', methods=['POST'])
@jwt_required()
def book_room():
    data = request.get_json()
    if not data or 'room_id' not in data or 'date_start' not in data or 'date_end' not in data:
        abort(400, description="Missing required fields: room_id, date_start, date_end.")

    user_id = get_jwt_identity()
    room_id = data['room_id']
    date_start = data['date_start']
    date_end = data['date_end']

    # TODO: Add logic to check for room availability and create a booking record
    # For now, we'll just return a success message

    return standardized_response(message="Room booked successfully.", status_code=201)

@booking_bp.route('/rent-car', methods=['POST'])
@jwt_required()
def rent_car():
    data = request.get_json()
    if not data or 'car_id' not in data or 'date_start' not in data or 'date_end' not in data:
        abort(400, description="Missing required fields: car_id, date_start, date_end.")

    user_id = get_jwt_identity()
    car_id = data['car_id']
    date_start = data['date_start']
    date_end = data['date_end']

    # TODO: Add logic to check for car availability and create a rental record
    # For now, we'll just return a success message

    return standardized_response(message="Car rented successfully.", status_code=201)
