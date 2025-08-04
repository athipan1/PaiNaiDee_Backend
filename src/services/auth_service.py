from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from src.models import db, User


class AuthService:
    @staticmethod
    def register_user(username, email, password):
        # Check if user already exists by username or email
        if User.query.filter_by(username=username).first():
            return None, "User with this username already exists."
        
        if User.query.filter_by(email=email).first():
            return None, "User with this email already exists."

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user, "User created successfully."

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return None

        access_token = create_access_token(identity=str(user.id))
        return access_token

    @staticmethod
    def register_admin(username, email, password):
        # Check if admin already exists by username or email
        if User.query.filter_by(username=username).first():
            return None, "Admin with this username already exists."
        
        if User.query.filter_by(email=email).first():
            return None, "Admin with this email already exists."

        hashed_password = generate_password_hash(password)
        new_admin = User(
            username=username, 
            email=email, 
            password=hashed_password,
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        return new_admin, "Admin created successfully."

    @staticmethod
    def login_admin(email, password):
        admin = User.query.filter_by(email=email, is_admin=True).first()

        if not admin or not check_password_hash(admin.password, password):
            return None

        access_token = create_access_token(identity=str(admin.id))
        return access_token
