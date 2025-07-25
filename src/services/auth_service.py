from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from src.models import db, User


class AuthService:
    @staticmethod
    def register_user(username, password):
        if User.query.filter_by(username=username).first():
            return None, "User already exists."

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user, "User created successfully."

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return None

        access_token = create_access_token(identity=str(user.id))
        return access_token
