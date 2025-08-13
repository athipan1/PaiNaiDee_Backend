from app.services.auth_service import AuthService
from app.services.review_service import ReviewService
from app.services.booking_service import BookingService
from app.models import db, Attraction, Room, Car
from werkzeug.security import check_password_hash


def test_register_user_success(app):
    with app.app_context():
        user, message = AuthService.register_user("newuser", "password")
        assert user is not None
        assert message == "User created successfully."
        assert user.username == "newuser"
        assert check_password_hash(user.password, "password")


def test_register_user_already_exists(app, test_user):
    with app.app_context():
        user, message = AuthService.register_user(
            "testuser", "password"
        )
        assert user is None
        assert message == "User already exists."


def test_login_user_success(app, test_user):
    with app.app_context():
        access_token = AuthService.login_user("testuser", "testpassword")
        assert access_token is not None


def test_login_user_invalid_credentials(app):
    with app.app_context():
        access_token = AuthService.login_user("testuser", "wrongpassword")
        assert access_token is None


def test_add_review_success(app, test_user):
    with app.app_context():
        attraction = Attraction(
            name="Test Attraction", province="Test Province"
        )
        db.session.add(attraction)
        db.session.commit()
        data = {"place_id": attraction.id, "rating": 5, "comment": "Great!"}
        review, message = ReviewService.add_review(test_user.id, data)
        assert review is not None
        assert message == "Review added successfully."
        assert review.rating == 5


def test_add_review_user_not_found(app):
    with app.app_context():
        data = {"place_id": 1, "rating": 5, "comment": "Great!"}
        review, message = ReviewService.add_review(999, data)
        assert review is None
        assert message == "User not found."


def test_book_room_success(app, test_user):
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        room = Room(name="Test Room", price=1000, attraction_id=attraction.id)
        db.session.add(room)
        db.session.commit()
        data = {
            "room_id": room.id,
            "date_start": "2024-01-01",
            "date_end": "2024-01-03",
        }
        success, message = BookingService.book_room(test_user.id, data)
        assert success is True
        assert message == "Room booked successfully."


def test_rent_car_success(app, test_user):
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        car = Car(brand="Test Car", price_per_day=500, attraction_id=attraction.id)
        db.session.add(car)
        db.session.commit()
        data = {"car_id": car.id, "date_start": "2024-01-01", "date_end": "2024-01-03"}
        success, message = BookingService.rent_car(test_user.id, data)
        assert success is True
        assert message == "Car rented successfully."


def test_book_room_conflict(app, test_user):
    """Test that booking a room with conflicting dates fails."""
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        room = Room(name="Test Room", price=1000, attraction_id=attraction.id)
        db.session.add(room)
        db.session.commit()
        
        # Create first booking
        data1 = {
            "room_id": room.id,
            "date_start": "2024-01-01",
            "date_end": "2024-01-05",
        }
        success1, message1 = BookingService.book_room(test_user.id, data1)
        assert success1 is True
        
        # Try to book overlapping dates
        data2 = {
            "room_id": room.id,
            "date_start": "2024-01-03",
            "date_end": "2024-01-07",
        }
        success2, message2 = BookingService.book_room(test_user.id, data2)
        assert success2 is False
        assert "not available" in message2


def test_rent_car_conflict(app, test_user):
    """Test that renting a car with conflicting dates fails."""
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        car = Car(brand="Test Car", price_per_day=500, attraction_id=attraction.id)
        db.session.add(car)
        db.session.commit()
        
        # Create first rental
        data1 = {
            "car_id": car.id,
            "date_start": "2024-01-01",
            "date_end": "2024-01-05",
        }
        success1, message1 = BookingService.rent_car(test_user.id, data1)
        assert success1 is True
        
        # Try to rent overlapping dates
        data2 = {
            "car_id": car.id,
            "date_start": "2024-01-03",
            "date_end": "2024-01-07",
        }
        success2, message2 = BookingService.rent_car(test_user.id, data2)
        assert success2 is False
        assert "not available" in message2


def test_book_room_nonexistent_room(app, test_user):
    """Test booking a room that doesn't exist."""
    with app.app_context():
        data = {
            "room_id": 999,
            "date_start": "2024-01-01",
            "date_end": "2024-01-03",
        }
        success, message = BookingService.book_room(test_user.id, data)
        assert success is False
        assert "Room not found" in message


def test_rent_car_nonexistent_car(app, test_user):
    """Test renting a car that doesn't exist."""
    with app.app_context():
        data = {
            "car_id": 999,
            "date_start": "2024-01-01",
            "date_end": "2024-01-03",
        }
        success, message = BookingService.rent_car(test_user.id, data)
        assert success is False
        assert "Car not found" in message


def test_book_room_invalid_dates(app, test_user):
    """Test booking with invalid date range."""
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        room = Room(name="Test Room", price=1000, attraction_id=attraction.id)
        db.session.add(room)
        db.session.commit()
        
        data = {
            "room_id": room.id,
            "date_start": "2024-01-05",
            "date_end": "2024-01-03",  # End before start
        }
        success, message = BookingService.book_room(test_user.id, data)
        assert success is False
        assert "Start date must be before end date" in message


def test_rent_car_invalid_dates(app, test_user):
    """Test car rental with invalid date range."""
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        car = Car(brand="Test Car", price_per_day=500, attraction_id=attraction.id)
        db.session.add(car)
        db.session.commit()
        
        data = {
            "car_id": car.id,
            "date_start": "2024-01-05",
            "date_end": "2024-01-03",  # End before start
        }
        success, message = BookingService.rent_car(test_user.id, data)
        assert success is False
        assert "Start date must be before end date" in message
