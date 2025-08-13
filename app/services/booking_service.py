
from ..models import db, Room, Car, RoomBooking, CarRental
from sqlalchemy import and_
from datetime import datetime


class BookingService:
    @staticmethod
    def _parse_date(date_value):
        """Convert string date to date object if needed."""
        if isinstance(date_value, str):
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        return date_value

    @staticmethod
    def book_room(user_id, data):
        """
        Book a room with availability checking and booking record creation.
        """
        room_id = data["room_id"]
        date_start = BookingService._parse_date(data["date_start"])
        date_end = BookingService._parse_date(data["date_end"])

        # Validate date range
        if date_start >= date_end:
            return False, "Start date must be before end date."

        # Check if room exists
        room = db.session.get(Room, room_id)
        if not room:
            return False, "Room not found."

        # Check for existing bookings that conflict with the requested dates
        conflicting_booking = (
            db.session.query(RoomBooking)
            .filter(
                and_(
                    RoomBooking.room_id == room_id,
                    RoomBooking.status == "active",
                    # Check for any overlap in date ranges
                    RoomBooking.date_start < date_end,
                    RoomBooking.date_end > date_start,
                )
            )
            .first()
        )

        if conflicting_booking:
            return False, "Room is not available for the selected dates."

        # Create the booking
        try:
            booking = RoomBooking(
                user_id=user_id,
                room_id=room_id,
                date_start=date_start,
                date_end=date_end,
            )
            db.session.add(booking)
            db.session.commit()
            return True, "Room booked successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to create booking: {str(e)}"

    @staticmethod
    def rent_car(user_id, data):
        """
        Rent a car with availability checking and rental record creation.
        """
        car_id = data["car_id"]
        date_start = BookingService._parse_date(data["date_start"])
        date_end = BookingService._parse_date(data["date_end"])

        # Validate date range
        if date_start >= date_end:
            return False, "Start date must be before end date."

        # Check if car exists
        car = db.session.get(Car, car_id)
        if not car:
            return False, "Car not found."

        # Check for existing rentals that conflict with the requested dates
        conflicting_rental = (
            db.session.query(CarRental)
            .filter(
                and_(
                    CarRental.car_id == car_id,
                    CarRental.status == "active",
                    # Check for any overlap in date ranges
                    CarRental.date_start < date_end,
                    CarRental.date_end > date_start,
                )
            )
            .first()
        )

        if conflicting_rental:
            return False, "Car is not available for the selected dates."

        # Create the rental
        try:
            rental = CarRental(
                user_id=user_id,
                car_id=car_id,
                date_start=date_start,
                date_end=date_end,
            )
            db.session.add(rental)
            db.session.commit()
            return True, "Car rented successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to create rental: {str(e)}"
