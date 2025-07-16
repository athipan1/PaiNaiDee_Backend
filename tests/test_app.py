import pytest
from src.app import create_app
from src.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        from src.models import db
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    """Test the home page."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Welcome to Pai Nai Dee Backend!" in rv.data

def test_attractions_endpoint(client):
    """Test the attractions endpoint."""
    rv = client.get('/api/attractions')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert isinstance(json_data, list)

def test_add_attraction(client):
    """Test adding a new attraction."""
    new_attraction = {
        "name": "Test Temple",
        "description": "A beautiful test temple.",
        "province": "Test Province",
        "category": "Temple",
        "image_urls": ["http://example.com/image.jpg"]
    }
    rv = client.post('/api/attractions', json=new_attraction)
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['message'] == 'Attraction added successfully'
    assert 'id' in json_data

    # Verify the attraction was added
    rv = client.get('/api/attractions')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert len(json_data) == 1
    assert json_data[0]['name'] == 'Test Temple'
