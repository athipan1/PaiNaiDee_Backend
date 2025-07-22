import io
import pytest
from src.app import create_app
from src.models import db, Attraction, User, Room, Car
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

from flask_jwt_extended import JWTManager

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            hashed_password = generate_password_hash("testpassword")
            user = User(username="testuser", password=hashed_password)
            db.session.add(user)
            db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {access_token}'}
        return headers

def test_home_page(client):
    """Test the home page."""
    rv = client.get('/')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert "Welcome to Pai Nai Dii Backend!" in json_data['message']

def test_get_all_attractions(client):
    """Test the attractions endpoint."""
    rv = client.get('/api/attractions')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'attractions' in json_data['data']
    assert 'pagination' in json_data['data']

def test_add_attraction(client, auth_headers):
    """Test adding a new attraction."""
    data = {
        'name': 'Test Temple',
        'description': 'A beautiful test temple.',
        'province': 'Test Province',
        'category': 'Temple',
        'cover_image': (io.BytesIO(b"abcdef"), 'test.jpg')
    }

    rv = client.post('/api/attractions', headers=auth_headers, data=data, content_type='multipart/form-data')
    if rv.status_code != 201:
        print(rv.get_json())
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Attraction added successfully' in json_data['message']
    assert 'id' in json_data['data']

def test_update_attraction(client, app):
    """Test updating an attraction."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        # Add an attraction to update
        attraction = Attraction(name="Old Name", description="Old Description", province="Old Province")
        db.session.add(attraction)
        db.session.commit()
        attraction_id = attraction.id

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    update_data = {
        "name": "New Name",
        "description": "New Description"
    }

    rv = client.put(f'/api/attractions/{attraction_id}', headers=headers, json=update_data)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Attraction updated successfully' in json_data['message']
    assert json_data['data']['name'] == 'New Name'

def test_delete_attraction(client, app):
    """Test deleting an attraction."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=str(test_user.id))

        # Add an attraction to delete
        attraction = Attraction(name="To Be Deleted", description="Delete me", province="Delete Province")
        db.session.add(attraction)
        db.session.commit()
        attraction_id = attraction.id

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    rv = client.delete(f'/api/attractions/{attraction_id}', headers=headers)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Attraction deleted successfully' in json_data['message']

def test_get_attraction_detail_with_rooms_and_cars(client, app):
    """Test getting attraction detail with rooms and cars."""
    with app.app_context():
        attraction = Attraction(name="Test Attraction", description="Test Description", province="Test Province")
        db.session.add(attraction)
        db.session.commit()

        room = Room(name="Test Room", price=1000, attraction_id=attraction.id)
        car = Car(brand="Test Car", price_per_day=500, attraction_id=attraction.id)
        db.session.add(room)
        db.session.add(car)
        db.session.commit()

        rv = client.get(f'/api/attractions/{attraction.id}')
        assert rv.status_code == 200
        json_data = rv.get_json()
        assert json_data['success'] is True
        assert 'rooms' in json_data['data']
        assert 'cars' in json_data['data']
        assert len(json_data['data']['rooms']) == 1
        assert len(json_data['data']['cars']) == 1
        assert json_data['data']['rooms'][0]['name'] == 'Test Room'
        assert json_data['data']['cars'][0]['brand'] == 'Test Car'

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

    data = {
        "room_id": room_id,
        "date_start": "2024-01-01",
        "date_end": "2024-01-03"
    }
    rv = client.post('/api/book-room', headers=auth_headers, json=data)
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Room booked successfully' in json_data['message']

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

    data = {
        "car_id": car_id,
        "date_start": "2024-01-01",
        "date_end": "2024-01-03"
    }
    rv = client.post('/api/rent-car', headers=auth_headers, json=data)
    if rv.status_code != 201:
        print(rv.get_json())
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Car rented successfully' in json_data['message']
