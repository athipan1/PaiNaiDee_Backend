from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from src.services.room_service import RoomService
from src.utils.response import standardized_response
from marshmallow import ValidationError

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/rooms", methods=["GET"])
def get_all_rooms():
    """
    Get all rooms with optional filtering
    ---
    tags:
      - Rooms
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
      - name: near
        in: query
        type: integer
        description: Filter rooms near a specific attraction ID
      - name: min_price
        in: query
        type: number
        description: Minimum price filter
      - name: max_price
        in: query
        type: number
        description: Maximum price filter
    responses:
      200:
        description: List of rooms retrieved successfully
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
                rooms:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      price:
                        type: number
                      attraction_id:
                        type: integer
                      attraction_name:
                        type: string
                      attraction_address:
                        type: string
                      attraction_location:
                        type: object
                        properties:
                          lat:
                            type: number
                          lng:
                            type: number
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
    near_attraction_id = request.args.get("near", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    paginated_rooms = RoomService.get_all_rooms(
        page=page,
        limit=limit,
        near_attraction_id=near_attraction_id,
        min_price=min_price,
        max_price=max_price
    )

    # Format room data with attraction information
    rooms_data = []
    for room_result in paginated_rooms.items:
        room = room_result.Room
        room_data = {
            "id": room.id,
            "name": room.name,
            "price": room.price,
            "attraction_id": room.attraction_id,
            "attraction_name": room_result.attraction_name,
            "attraction_address": room_result.attraction_address,
            "attraction_location": {
                "lat": room_result.attraction_latitude,
                "lng": room_result.attraction_longitude
            },
            "attraction_province": room_result.attraction_province
        }
        rooms_data.append(room_data)

    pagination_data = {
        "total_pages": paginated_rooms.pages,
        "current_page": paginated_rooms.page,
        "total_items": paginated_rooms.total,
        "has_next": paginated_rooms.has_next,
        "has_prev": paginated_rooms.has_prev,
    }

    return standardized_response(
        data={"rooms": rooms_data, "pagination": pagination_data},
        message="Rooms retrieved successfully.",
    )


@rooms_bp.route("/rooms/<int:room_id>", methods=["GET"])
def get_room_detail(room_id):
    """
    Get detailed information about a specific room
    ---
    tags:
      - Rooms
    parameters:
      - name: room_id
        in: path
        type: integer
        required: true
        description: ID of the room to retrieve
    responses:
      200:
        description: Room details retrieved successfully
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
                price:
                  type: number
                attraction_id:
                  type: integer
                attraction_name:
                  type: string
                attraction_address:
                  type: string
                attraction_location:
                  type: object
                  properties:
                    lat:
                      type: number
                    lng:
                      type: number
      404:
        description: Room not found
    """
    room_result = RoomService.get_room_by_id(room_id)
    room = room_result.Room
    
    room_data = {
        "id": room.id,
        "name": room.name,
        "price": room.price,
        "attraction_id": room.attraction_id,
        "attraction_name": room_result.attraction_name,
        "attraction_address": room_result.attraction_address,
        "attraction_location": {
            "lat": room_result.attraction_latitude,
            "lng": room_result.attraction_longitude
        },
        "attraction_province": room_result.attraction_province
    }
    
    return standardized_response(
        data=room_data,
        message="Room details retrieved successfully.",
    )


@rooms_bp.route("/rooms", methods=["POST"])
@jwt_required()
def create_room():
    """
    Create a new room
    ---
    tags:
      - Rooms
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - attraction_id
            - name
            - price
          properties:
            attraction_id:
              type: integer
              description: ID of the attraction this room belongs to
            name:
              type: string
              description: Name of the room
            price:
              type: number
              description: Price per night for the room
    responses:
      201:
        description: Room created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
      400:
        description: Invalid input data
      401:
        description: Authentication required
    """
    data = request.get_json()
    
    # Basic validation
    required_fields = ['attraction_id', 'name', 'price']
    for field in required_fields:
        if field not in data:
            return standardized_response(
                success=False,
                message=f"Missing required field: {field}",
                status_code=400
            )
    
    try:
        new_room = RoomService.create_room(data)
        return standardized_response(
            data=new_room.to_dict(),
            message="Room created successfully.",
            status_code=201
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error creating room: {str(e)}",
            status_code=400
        )


@rooms_bp.route("/rooms/<int:room_id>", methods=["PUT"])
@jwt_required()
def update_room(room_id):
    """
    Update an existing room
    ---
    tags:
      - Rooms
    security:
      - JWT: []
    parameters:
      - name: room_id
        in: path
        type: integer
        required: true
        description: ID of the room to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: Name of the room
            price:
              type: number
              description: Price per night for the room
    responses:
      200:
        description: Room updated successfully
      400:
        description: Invalid input data
      401:
        description: Authentication required
      404:
        description: Room not found
    """
    data = request.get_json()
    
    try:
        updated_room = RoomService.update_room(room_id, data)
        return standardized_response(
            data=updated_room.to_dict(),
            message="Room updated successfully."
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error updating room: {str(e)}",
            status_code=400
        )


@rooms_bp.route("/rooms/<int:room_id>", methods=["DELETE"])
@jwt_required()
def delete_room(room_id):
    """
    Delete a room
    ---
    tags:
      - Rooms
    security:
      - JWT: []
    parameters:
      - name: room_id
        in: path
        type: integer
        required: true
        description: ID of the room to delete
    responses:
      200:
        description: Room deleted successfully
      401:
        description: Authentication required
      404:
        description: Room not found
    """
    try:
        RoomService.delete_room(room_id)
        return standardized_response(
            message="Room deleted successfully."
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error deleting room: {str(e)}",
            status_code=400
        )


@rooms_bp.route("/rooms/<int:room_id>/availability", methods=["GET"])
def check_room_availability(room_id):
    """
    Check room availability for specific dates
    ---
    tags:
      - Rooms
    parameters:
      - name: room_id
        in: path
        type: integer
        required: true
        description: ID of the room to check
      - name: date_start
        in: query
        type: string
        format: date
        required: true
        description: Start date (YYYY-MM-DD)
      - name: date_end
        in: query
        type: string
        format: date
        required: true
        description: End date (YYYY-MM-DD)
    responses:
      200:
        description: Availability status retrieved successfully
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
                available:
                  type: boolean
                room_id:
                  type: integer
                date_start:
                  type: string
                date_end:
                  type: string
      400:
        description: Invalid date parameters
      404:
        description: Room not found
    """
    date_start = request.args.get("date_start")
    date_end = request.args.get("date_end")
    
    if not date_start or not date_end:
        return standardized_response(
            success=False,
            message="Both date_start and date_end parameters are required",
            status_code=400
        )
    
    try:
        is_available = RoomService.get_room_availability(room_id, date_start, date_end)
        return standardized_response(
            data={
                "available": is_available,
                "room_id": room_id,
                "date_start": date_start,
                "date_end": date_end
            },
            message="Room availability checked successfully."
        )
    except Exception as e:
        return standardized_response(
            success=False,
            message=f"Error checking availability: {str(e)}",
            status_code=400
        )