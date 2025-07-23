from src.models import db, User
from werkzeug.security import generate_password_hash


def test_login(client, app):
    """Test the login endpoint."""
    with app.app_context():
        hashed_password = generate_password_hash("testpassword")
        test_user = User(username="testuser", password=hashed_password)
        db.session.add(test_user)
        db.session.commit()

    login_data = {"username": "testuser", "password": "testpassword"}

    rv = client.post("/api/auth/login", json=login_data)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["success"] is True
    assert "access_token" in json_data["data"]
