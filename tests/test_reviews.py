import json
import pytest
from src.app import create_app
from src.models import db, Review

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_add_review_success(client):
    """Test adding a review successfully."""
    response = client.post('/api/reviews',
                           data=json.dumps({
                               "place_id": 1,
                               "user_name": "Test User",
                               "rating": 5,
                               "comment": "Great place!"
                           }),
                           content_type='application/json')
    assert response.status_code == 201
    assert response.json['message'] == "รีวิวถูกบันทึกแล้ว"

def test_add_review_invalid_rating(client):
    """Test adding a review with an invalid rating."""
    response = client.post('/api/reviews',
                           data=json.dumps({
                               "place_id": 1,
                               "user_name": "Test User",
                               "rating": 6,
                               "comment": "Great place!"
                           }),
                           content_type='application/json')
    assert response.status_code == 400
    assert response.json['message'] == "Rating must be between 1 and 5"

def test_add_review_long_comment(client):
    """Test adding a review with a comment that is too long."""
    long_comment = "a" * 501
    response = client.post('/api/reviews',
                           data=json.dumps({
                               "place_id": 1,
                               "user_name": "Test User",
                               "rating": 5,
                               "comment": long_comment
                           }),
                           content_type='application/json')
    assert response.status_code == 400
    assert response.json['message'] == "Comment must not exceed 500 characters"

def test_add_review_missing_data(client):
    """Test adding a review with missing data."""
    response = client.post('/api/reviews',
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400
    assert response.json['message'] == "Invalid data"
