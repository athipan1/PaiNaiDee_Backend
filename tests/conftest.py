import pytest
from src.app import create_app
from src.models import db, User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="function")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def test_user(app):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            hashed_password = generate_password_hash("testpassword")
            user = User(username="testuser", password=hashed_password)
            db.session.add(user)
            db.session.commit()
        user = User.query.filter_by(username="testuser").first()
        return user


@pytest.fixture(scope="function")
def auth_headers(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user.id)
        access_token = create_access_token(identity=str(user.id))
        headers = {"Authorization": f"Bearer {access_token}"}
        return headers
