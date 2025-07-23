import pytest
from marshmallow import ValidationError
from src.schemas.auth import RegisterSchema, LoginSchema
from src.schemas.review import ReviewSchema
from src.schemas.booking import RoomBookingSchema, CarRentalSchema
from src.schemas.attraction import AttractionSchema


def test_register_schema_valid():
    schema = RegisterSchema()
    data = {"username": "testuser", "password": "password"}
    result = schema.load(data)
    assert result == data


def test_register_schema_invalid():
    schema = RegisterSchema()
    with pytest.raises(ValidationError):
        schema.load({"username": "a"})
    with pytest.raises(ValidationError):
        schema.load({"password": "a"})


def test_login_schema_valid():
    schema = LoginSchema()
    data = {"username": "testuser", "password": "password"}
    result = schema.load(data)
    assert result == data


def test_login_schema_invalid():
    schema = LoginSchema()
    with pytest.raises(ValidationError):
        schema.load({"username": ""})
    with pytest.raises(ValidationError):
        schema.load({"password": ""})


def test_review_schema_valid():
    schema = ReviewSchema()
    data = {"place_id": 1, "rating": 5, "comment": "Great!"}
    result = schema.load(data)
    assert result == data


def test_review_schema_invalid():
    schema = ReviewSchema()
    with pytest.raises(ValidationError):
        schema.load({"place_id": 1, "rating": 6})
    with pytest.raises(ValidationError):
        schema.load({"place_id": 1, "rating": 0})
    with pytest.raises(ValidationError):
        schema.load({"place_id": 1, "rating": 5, "comment": "a" * 501})


def test_room_booking_schema_valid():
    schema = RoomBookingSchema()
    data = {"room_id": 1, "date_start": "2024-01-01", "date_end": "2024-01-03"}
    result = schema.load(data)
    assert result["room_id"] == data["room_id"]


def test_room_booking_schema_invalid():
    schema = RoomBookingSchema()
    with pytest.raises(ValidationError):
        schema.load({"room_id": 1, "date_start": "2024-01-01"})


def test_car_rental_schema_valid():
    schema = CarRentalSchema()
    data = {"car_id": 1, "date_start": "2024-01-01", "date_end": "2024-01-03"}
    result = schema.load(data)
    assert result["car_id"] == data["car_id"]


def test_car_rental_schema_invalid():
    schema = CarRentalSchema()
    with pytest.raises(ValidationError):
        schema.load({"car_id": 1, "date_start": "2024-01-01"})


def test_attraction_schema_valid():
    schema = AttractionSchema()
    data = {
        "name": "Test Temple",
        "description": "A beautiful test temple.",
        "province": "Test Province",
        "category": "Temple",
    }
    result = schema.load(data)
    assert result == data


def test_attraction_schema_invalid():
    schema = AttractionSchema()
    with pytest.raises(ValidationError):
        schema.load({"name": "a"})
    with pytest.raises(ValidationError):
        schema.load({"description": ""})
    with pytest.raises(ValidationError):
        schema.load({"province": ""})
    with pytest.raises(ValidationError):
        schema.load({"category": ""})
