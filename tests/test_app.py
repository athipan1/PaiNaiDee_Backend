import pytest
from src.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

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
    assert len(json_data) > 0
    assert 'name' in json_data[0]
