from src.models import db, User, Attraction
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


def test_add_review_success(client, app):
    """Test adding a review successfully."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        place_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 5, "comment": "Great place!"},
        headers=headers,
    )
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "Review added successfully" in json_data["message"]


def test_add_review_unauthorized(client):
    """Test adding a review without authorization."""
    response = client.post(
        "/api/reviews", json={"place_id": 1, "rating": 5, "comment": "Great place!"}
    )
    assert response.status_code == 401
