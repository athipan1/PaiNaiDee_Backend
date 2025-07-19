import pytest
from src.app import create_app
from src.models import db, User
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

def test_login(client, app):
    """Test the login endpoint."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    rv = client.post('/api/auth/login', json=login_data)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'access_token' in json_data['data']
