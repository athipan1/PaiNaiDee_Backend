import io
from app.models import db, Attraction, User, Room, Car
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


def test_home_page(client):
    """Test the home page."""
    rv = client.get("/")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "Welcome to PaiNaiDee Backend!" in json_data["message"]


def test_get_all_attractions(client):
    """Test the attractions endpoint."""
    rv = client.get("/api/attractions")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "attractions" in json_data["data"]
    assert "pagination" in json_data["data"]


def test_add_attraction(client, auth_headers):
    """Test adding a new attraction."""
    data = {
        "name": "Test Temple",
        "description": "A beautiful test temple.",
        "province": "Test Province",
        "category": "Temple",
        "cover_image": (io.BytesIO(b"abcdef"), "test.jpg"),
    }

    rv = client.post(
        "/api/attractions",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    if rv.status_code != 201:
        print(rv.get_json())
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "Attraction added successfully" in json_data["message"]
    assert "id" in json_data["data"]


def test_update_attraction(client, app):
    """Test updating an attraction."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        # Add an attraction to update
        attraction = Attraction(
            name="Old Name", description="Old Description", province="Old Province"
        )
        db.session.add(attraction)
        db.session.commit()
        attraction_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}

    update_data = {"name": "New Name", "description": "New Description"}

    rv = client.put(
        f"/api/attractions/{attraction_id}", headers=headers, json=update_data
    )
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "Attraction updated successfully" in json_data["message"]
    assert json_data["data"]["name"] == "New Name"


def test_delete_attraction(client, app):
    """Test deleting an attraction."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        # Add an attraction to delete
        attraction = Attraction(
            name="To Be Deleted", description="Delete me", province="Delete Province"
        )
        db.session.add(attraction)
        db.session.commit()
        attraction_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}

    rv = client.delete(f"/api/attractions/{attraction_id}", headers=headers)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "Attraction deleted successfully" in json_data["message"]


def test_get_attraction_detail_with_rooms_and_cars(client, app):
    """Test getting attraction detail with rooms and cars."""
    with app.app_context():
        attraction = Attraction(
            name="Test Attraction",
            description="Test Description",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()

        room = Room(name="Test Room", price=1000, attraction_id=attraction.id)
        car = Car(brand="Test Car", price_per_day=500, attraction_id=attraction.id)
        db.session.add(room)
        db.session.add(car)
        db.session.commit()

        rv = client.get(f"/api/attractions/{attraction.id}")
        assert rv.status_code == 200
        json_data = rv.get_json()
        assert json_data["success"] is True
        assert "rooms" in json_data["data"]
        assert "cars" in json_data["data"]
        assert "average_rating" in json_data["data"]
        assert "total_reviews" in json_data["data"]
        assert json_data["data"]["average_rating"] == 0
        assert json_data["data"]["total_reviews"] == 0


def test_get_attraction_detail_with_reviews(client, app):
    """Test getting attraction detail with reviews and rating."""
    with app.app_context():
        # Create user and attraction
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        
        attraction = Attraction(
            name="Test Resort",
            description="A test resort with reviews",
            province="Test Province",
        )
        db.session.add(attraction)
        db.session.commit()
        
        access_token = create_access_token(identity=str(test_user.id))
        attraction_id = attraction.id

    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add a review
    client.post(
        "/api/reviews",
        json={"place_id": attraction_id, "rating": 4, "comment": "Great place!"},
        headers=headers,
    )
    
    # Get attraction detail
    response = client.get(f"/api/attractions/{attraction_id}")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["average_rating"] == 4.0
    assert json_data["data"]["total_reviews"] == 1


def test_book_room(client, auth_headers, app):
    """Test booking a room."""
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        room = Room(name="Test Room", price=1000, attraction_id=attraction.id)
        db.session.add(room)
        db.session.commit()
        room_id = room.id

    data = {"room_id": room_id, "date_start": "2024-01-01", "date_end": "2024-01-03"}
    rv = client.post("/api/book-room", headers=auth_headers, json=data)
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "Room booked successfully" in json_data["message"]


def test_rent_car(client, auth_headers, app):
    """Test renting a car."""
    with app.app_context():
        attraction = Attraction(name="Test Attraction", province="Test Province")
        db.session.add(attraction)
        db.session.commit()
        car = Car(brand="Test Car", price_per_day=500, attraction_id=attraction.id)
        db.session.add(car)
        db.session.commit()
        car_id = car.id

    data = {"car_id": car_id, "date_start": "2024-01-01", "date_end": "2024-01-03"}
    rv = client.post("/api/rent-car", headers=auth_headers, json=data)
    if rv.status_code != 201:
        print(rv.get_json())
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "Car rented successfully" in json_data["message"]


def test_get_attractions_by_category(client, app):
    """Test getting attractions by category - public access."""
    with app.app_context():
        # Create test attractions with different categories
        attraction1 = Attraction(
            name="หาดบางแสน",
            province="ชลบุรี",
            category="ชายหาด",
            main_image_url="https://example.com/beach1.jpg"
        )
        attraction2 = Attraction(
            name="หาดแม่รำพึง",
            province="ระยอง", 
            category="ชายหาด",
            main_image_url="https://example.com/beach2.jpg"
        )
        attraction3 = Attraction(
            name="วัดพระแก้ว",
            province="กรุงเทพฯ",
            category="วัด",
            main_image_url="https://example.com/temple1.jpg"
        )
        
        db.session.add_all([attraction1, attraction2, attraction3])
        db.session.commit()

    # Test getting beaches
    rv = client.get("/api/attractions/category/ชายหาด")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 2
    
    # Verify response structure
    beach_data = json_data["data"]
    for item in beach_data:
        assert "id" in item
        assert "name" in item
        assert "province" in item
        assert "thumbnail" in item
        
    # Verify specific data
    beach_names = [item["name"] for item in beach_data]
    assert "หาดบางแสน" in beach_names
    assert "หาดแม่รำพึง" in beach_names


def test_get_attractions_by_category_case_insensitive(client, app):
    """Test category search is case insensitive."""
    with app.app_context():
        attraction = Attraction(
            name="วัดอรุณ",
            province="กรุงเทพฯ",
            category="วัด",
            main_image_url="https://example.com/temple.jpg"
        )
        db.session.add(attraction)
        db.session.commit()

    # Test with different case
    rv = client.get("/api/attractions/category/วัด")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["name"] == "วัดอรุณ"


def test_get_attractions_by_category_empty_result(client):
    """Test category endpoint with no matching results."""
    rv = client.get("/api/attractions/category/nonexistent")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 0


def test_get_attractions_by_category_partial_match(client, app):
    """Test category search with partial matching."""
    with app.app_context():
        attraction = Attraction(
            name="ภูเขาไฟ",
            province="เชียงใหม่",
            category="ภูเขาและป่าไผ่",
            main_image_url="https://example.com/mountain.jpg"
        )
        db.session.add(attraction)
        db.session.commit()

    # Test partial match
    rv = client.get("/api/attractions/category/ภูเขา")
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["name"] == "ภูเขาไฟ"
