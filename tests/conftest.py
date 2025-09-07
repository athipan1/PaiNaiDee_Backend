import pytest
from src.app import create_app
from src.models import db, User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


# Import the Base from the new Alembic-compatible setup
from app.db.session import Base


@pytest.fixture(scope="function")
def app():
    app = create_app("testing")
    with app.app_context():
        # Create tables from both metadata objects
        # The legacy 'db' object from src/models
        db.create_all()
        # The new 'Base' object from app/db/session
        Base.metadata.create_all(bind=db.engine)

        yield app

        db.session.remove()

        # Drop tables in reverse order of creation to respect foreign keys
        Base.metadata.drop_all(bind=db.engine)
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
