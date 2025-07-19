import io
import pytest
from src.app import create_app
from src.models import db, Attraction, User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

from flask_jwt_extended import JWTManager

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        JWTManager(app)
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=test_user.id)
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
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

def test_add_attraction(client, app):
    """Test adding a new attraction."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        access_token = create_access_token(identity=test_user.id)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    data = {
        'name': 'Test Temple',
        'description': 'A beautiful test temple.',
        'province': 'Test Province',
        'category': 'Temple',
        'cover_image': (io.BytesIO(b"abcdef"), 'test.jpg')
    }

    rv = client.post('/api/attractions', headers=headers, data=data, content_type='multipart/form-data')
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Attraction added successfully' in json_data['message']
    assert 'id' in json_data['data']

def test_update_attraction(client, auth_headers, app):
    """Test updating an attraction."""
    with app.app_context():
        # Add an attraction to update
        attraction = Attraction(name="Old Name", description="Old Description", province="Old Province")
        db.session.add(attraction)
        db.session.commit()
        attraction_id = attraction.id

    update_data = {
        "name": "New Name",
        "description": "New Description"
    }

    rv = client.put(f'/api/attractions/{attraction_id}', headers=auth_headers, json=update_data)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Attraction updated successfully' in json_data['message']
    assert json_data['data']['name'] == 'New Name'

def test_delete_attraction(client, auth_headers, app):
    """Test deleting an attraction."""
    with app.app_context():
        # Add an attraction to delete
        attraction = Attraction(name="To Be Deleted", description="Delete me", province="Delete Province")
        db.session.add(attraction)
        db.session.commit()
        attraction_id = attraction.id

    rv = client.delete(f'/api/attractions/{attraction_id}', headers=auth_headers)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Attraction deleted successfully' in json_data['message']
