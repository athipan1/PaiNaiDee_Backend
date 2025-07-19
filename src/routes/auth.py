from flask import Blueprint, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from src.models import db, User
from src.utils import standardized_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description="Missing username or password.")

    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        abort(409, description="User already exists.")

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return standardized_response(message="User created successfully.", status_code=201)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description="Missing username or password.")

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        abort(401, description="Invalid credentials.")

    access_token = create_access_token(identity=user.id)
    return standardized_response(data={'access_token': access_token}, message="Login successful.")
