from src.models import db, Room, Attraction
from sqlalchemy import func


class RoomService:
    @staticmethod
    def get_all_rooms(page=1, limit=10, near_attraction_id=None, min_price=None, max_price=None):
        """
        Get all rooms with optional filtering by attraction proximity and price range
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            near_attraction_id: Filter rooms near a specific attraction
            min_price: Minimum price filter
            max_price: Maximum price filter
        """
        query = Room.query
        
        # Filter by attraction if specified
        if near_attraction_id:
            query = query.filter(Room.attraction_id == near_attraction_id)
        
        # Filter by price range if specified
        if min_price is not None:
            query = query.filter(Room.price >= min_price)
        if max_price is not None:
            query = query.filter(Room.price <= max_price)
        
        # Join with attraction to get additional information
        query = query.join(Attraction).add_columns(
            Attraction.name.label('attraction_name'),
            Attraction.address.label('attraction_address'),
            Attraction.latitude.label('attraction_latitude'),
            Attraction.longitude.label('attraction_longitude'),
            Attraction.province.label('attraction_province')
        )
        
        paginated_rooms = query.order_by(Room.price).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return paginated_rooms
    
    @staticmethod
    def get_room_by_id(room_id):
        """Get a specific room by ID with attraction information"""
        room = db.session.query(Room).join(Attraction).add_columns(
            Attraction.name.label('attraction_name'),
            Attraction.address.label('attraction_address'),
            Attraction.latitude.label('attraction_latitude'),
            Attraction.longitude.label('attraction_longitude'),
            Attraction.province.label('attraction_province')
        ).filter(Room.id == room_id).first()
        
        if not room:
            from flask import abort
            abort(404, description="Room not found.")
        return room
    
    @staticmethod
    def get_rooms_near_attraction(attraction_id, page=1, limit=10):
        """Get rooms near a specific attraction"""
        return RoomService.get_all_rooms(
            page=page, 
            limit=limit, 
            near_attraction_id=attraction_id
        )
    
    @staticmethod
    def create_room(data):
        """Create a new room"""
        new_room = Room(
            attraction_id=data.get("attraction_id"),
            name=data.get("name"),
            price=data.get("price")
        )
        db.session.add(new_room)
        db.session.commit()
        return new_room
    
    @staticmethod
    def update_room(room_id, data):
        """Update an existing room"""
        room = db.session.get(Room, room_id)
        if not room:
            from flask import abort
            abort(404, description="Room not found.")
        
        for key, value in data.items():
            if hasattr(room, key):
                setattr(room, key, value)
        
        db.session.commit()
        return room
    
    @staticmethod
    def delete_room(room_id):
        """Delete a room"""
        room = db.session.get(Room, room_id)
        if not room:
            from flask import abort
            abort(404, description="Room not found.")
        
        db.session.delete(room)
        db.session.commit()
    
    @staticmethod
    def get_room_availability(room_id, date_start, date_end):
        """Check room availability for a date range"""
        from src.models.room_booking import RoomBooking
        from datetime import datetime
        
        # Convert string dates to date objects if needed
        if isinstance(date_start, str):
            date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        if isinstance(date_end, str):
            date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        
        # Check for existing bookings that overlap with the requested dates
        existing_booking = RoomBooking.query.filter(
            RoomBooking.room_id == room_id,
            RoomBooking.status == 'active',
            db.or_(
                db.and_(RoomBooking.date_start <= date_start, RoomBooking.date_end >= date_start),
                db.and_(RoomBooking.date_start <= date_end, RoomBooking.date_end >= date_end),
                db.and_(RoomBooking.date_start >= date_start, RoomBooking.date_end <= date_end)
            )
        ).first()
        
        return existing_booking is None