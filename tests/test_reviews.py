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


def test_add_duplicate_review_fails(client, app):
    """Test that user cannot review the same attraction twice."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        
        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        
        access_token = create_access_token(identity=str(test_user.id))
        place_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add first review
    response1 = client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 5, "comment": "Great place!"},
        headers=headers,
    )
    assert response1.status_code == 201
    
    # Try to add second review for same attraction
    response2 = client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 4, "comment": "Still good!"},
        headers=headers,
    )
    assert response2.status_code == 400


def test_get_attraction_reviews(client, app):
    """Test getting reviews for an attraction."""
    with app.app_context():
        # Create test user and attraction
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        
        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        
        # Create access token and add a review
        access_token = create_access_token(identity=str(test_user.id))
        place_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add a review first
    client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 4, "comment": "Nice place!"},
        headers=headers,
    )
    
    # Get reviews for the attraction
    response = client.get(f"/api/attractions/{place_id}/reviews")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "reviews" in json_data["data"]
    assert "average_rating" in json_data["data"]
    assert "total_reviews" in json_data["data"]
    assert json_data["data"]["total_reviews"] == 1
    assert json_data["data"]["average_rating"] == 4.0


def test_get_attraction_reviews_nonexistent_attraction(client):
    """Test getting reviews for non-existent attraction."""
    response = client.get("/api/attractions/99999/reviews")
    assert response.status_code == 500


def test_update_review_success(client, app):
    """Test updating a review successfully."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        
        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        
        access_token = create_access_token(identity=str(test_user.id))
        place_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add a review first
    response = client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 3, "comment": "OK place"},
        headers=headers,
    )
    assert response.status_code == 201
    
    # Get the review ID (we'll use the first review for this attraction)
    reviews_response = client.get(f"/api/attractions/{place_id}/reviews")
    review_id = reviews_response.get_json()["data"]["reviews"][0]["id"]
    
    # Update the review
    update_response = client.put(
        f"/api/reviews/{review_id}",
        json={"rating": 5, "comment": "Actually, it's great!"},
        headers=headers,
    )
    assert update_response.status_code == 200
    json_data = update_response.get_json()
    assert json_data["success"] is True
    assert "Review updated successfully" in json_data["message"]


def test_update_review_unauthorized(client, app):
    """Test updating someone else's review fails."""
    with app.app_context():
        # Create two users
        hashed_password = generate_password_hash("testpassword")
        test_user1 = User(username="testuser1", password=hashed_password)
        test_user2 = User(username="testuser2", password=hashed_password)
        db.session.add(test_user1)
        db.session.add(test_user2)
        
        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        
        access_token1 = create_access_token(identity=str(test_user1.id))
        access_token2 = create_access_token(identity=str(test_user2.id))
        place_id = attraction.id

    headers1 = {"Authorization": f"Bearer {access_token1}"}
    headers2 = {"Authorization": f"Bearer {access_token2}"}
    
    # User 1 adds a review
    client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 3, "comment": "OK place"},
        headers=headers1,
    )
    
    # Get the review ID
    reviews_response = client.get(f"/api/attractions/{place_id}/reviews")
    review_id = reviews_response.get_json()["data"]["reviews"][0]["id"]
    
    # User 2 tries to update User 1's review
    update_response = client.put(
        f"/api/reviews/{review_id}",
        json={"rating": 5, "comment": "Hacked!"},
        headers=headers2,
    )
    assert update_response.status_code == 403


def test_delete_review_success(client, app):
    """Test deleting a review successfully."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        
        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        
        access_token = create_access_token(identity=str(test_user.id))
        place_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add a review first
    response = client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 3, "comment": "OK place"},
        headers=headers,
    )
    assert response.status_code == 201
    
    # Get the review ID
    reviews_response = client.get(f"/api/attractions/{place_id}/reviews")
    review_id = reviews_response.get_json()["data"]["reviews"][0]["id"]
    
    # Delete the review
    delete_response = client.delete(f"/api/reviews/{review_id}", headers=headers)
    assert delete_response.status_code == 200
    json_data = delete_response.get_json()
    assert json_data["success"] is True
    assert "Review deleted successfully" in json_data["message"]


def test_delete_review_unauthorized(client, app):
    """Test deleting someone else's review fails."""
    with app.app_context():
        # Create two users
        hashed_password = generate_password_hash("testpassword")
        test_user1 = User(username="testuser1", password=hashed_password)
        test_user2 = User(username="testuser2", password=hashed_password)
        db.session.add(test_user1)
        db.session.add(test_user2)
        
        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        
        access_token1 = create_access_token(identity=str(test_user1.id))
        access_token2 = create_access_token(identity=str(test_user2.id))
        place_id = attraction.id

    headers1 = {"Authorization": f"Bearer {access_token1}"}
    headers2 = {"Authorization": f"Bearer {access_token2}"}
    
    # User 1 adds a review
    client.post(
        "/api/reviews",
        json={"place_id": place_id, "rating": 3, "comment": "OK place"},
        headers=headers1,
    )
    
    # Get the review ID
    reviews_response = client.get(f"/api/attractions/{place_id}/reviews")
    review_id = reviews_response.get_json()["data"]["reviews"][0]["id"]
    
    # User 2 tries to delete User 1's review
    delete_response = client.delete(f"/api/reviews/{review_id}", headers=headers2)
    assert delete_response.status_code == 403
