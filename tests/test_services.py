from src.services.auth_service import AuthService
from src.services.review_service import ReviewService
from src.services.booking_service import BookingService
from src.models import db, Attraction, Room, Car
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
