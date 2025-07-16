import pytest
import sys
import os

from src.app import create_app, home, get_all_attractions, get_attraction_detail, add_attraction
import json
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    app = create_app('development')
    app.config.update({
        "TESTING": True,
    })

    app.route('/')(home)
    app.route('/api/attractions', methods=['GET'])(get_all_attractions)
    app.route('/api/attractions/<int:attraction_id>', methods=['GET'])(get_attraction_detail)
    app.route('/api/attractions', methods=['POST'])(add_attraction)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    """Test the home page."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Welcome to Pai Nai Dii Backend!" in rv.data

@patch('src.app.get_db_connection')
def test_get_all_attractions(mock_get_db_connection, client):
    """Test the attractions endpoint."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [
        {'id': 1, 'name': 'Wat Arun', 'description': 'Temple of Dawn'}
    ]

    rv = client.get('/api/attractions')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) > 0
    assert 'name' in json_data[0]

@patch('src.app.get_db_connection')
def test_add_attraction(mock_get_db_connection, client):
    """Test adding a new attraction."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = [1]

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
