import pytest
from src.app import create_app
from src.models import db, User, Attraction
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

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

def test_add_review_success(client, app):
    """Test adding a review successfully."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        attraction = Attraction(name="Test Attraction", description="Test Description", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        place_id = attraction.id

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/reviews',
                           json={
                               "place_id": place_id,
                               "rating": 5,
                               "comment": "Great place!"
                           },
                           headers=headers)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['success'] is True
    assert "Review added successfully" in json_data['message']

def test_add_review_invalid_rating(client, app):
    """Test adding a review with an invalid rating."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        attraction = Attraction(name="Test Attraction", description="Test Description", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        place_id = attraction.id

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/reviews',
                           json={
                               "place_id": place_id,
                               "rating": 6,
                               "comment": "Great place!"
                           },
                           headers=headers)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['success'] is False
    assert "Rating must be between 1 and 5" in json_data['message']

def test_add_review_long_comment(client, app):
    """Test adding a review with a comment that is too long."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        attraction = Attraction(name="Test Attraction", description="Test Description", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        place_id = attraction.id

    headers = {'Authorization': f'Bearer {access_token}'}
    long_comment = "a" * 501
    response = client.post('/api/reviews',
                           json={
                               "place_id": place_id,
                               "rating": 5,
                               "comment": long_comment
                           },
                           headers=headers)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['success'] is False
    assert "Comment must not exceed 500 characters" in json_data['message']

def test_add_review_unauthorized(client):
    """Test adding a review without authorization."""
    response = client.post('/api/reviews',
                           json={
                               "place_id": 1,
                               "rating": 5,
                               "comment": "Great place!"
                           })
    assert response.status_code == 401
