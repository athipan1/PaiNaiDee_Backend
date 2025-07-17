import pytest
from src.app import create_app
from src.models import db
from unittest.mock import patch, MagicMock

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

def test_home_page(client):
    """Test the home page."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Welcome to Pai Nai Dii Backend!" in rv.data

def test_get_all_attractions(client):
    """Test the attractions endpoint."""
    rv = client.get('/api/attractions')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert isinstance(json_data, list)

@patch('src.models.db.session.add')
@patch('src.models.db.session.commit')
def test_add_attraction(mock_commit, mock_add, client):
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
    assert json_data['message'] == 'Added'
    assert 'id' in json_data
