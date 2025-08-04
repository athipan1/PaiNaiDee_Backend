from flask import Blueprint, request, abort
from src.services.auth_service import AuthService
from src.utils.response import standardized_response
from src.schemas.auth import RegisterSchema, LoginSchema, AdminRegisterSchema, AdminLoginSchema
from marshmallow import ValidationError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    try:
        validated_data = RegisterSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    username = validated_data["username"]
    email = validated_data["email"]
    password = validated_data["password"]

    user, message = AuthService.register_user(username, email, password)

    if not user:
        abort(409, description=message)

    return standardized_response(message=message, status_code=201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        validated_data = LoginSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    email = validated_data["email"]
    password = validated_data["password"]

    access_token = AuthService.login_user(email, password)

    if not access_token:
        abort(401, description="Invalid credentials.")

    return standardized_response(
        data={"access_token": access_token}, message="Login successful."
    )


@auth_bp.route("/admin/register", methods=["POST"])
def register_admin():
    """Register a new admin user"""
    data = request.get_json()
    try:
        validated_data = AdminRegisterSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    username = validated_data["username"]
    email = validated_data["email"]
    password = validated_data["password"]

    admin, message = AuthService.register_admin(username, email, password)

    if not admin:
        abort(409, description=message)

    return standardized_response(
        data={"admin_id": admin.id, "username": admin.username, "email": admin.email},
        message=message,
        status_code=201
    )


@auth_bp.route("/admin/login", methods=["POST"])
def login_admin():
    """Login for admin users"""
    data = request.get_json()
    try:
        validated_data = AdminLoginSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    email = validated_data["email"]
    password = validated_data["password"]

    access_token = AuthService.login_admin(email, password)

    if not access_token:
        abort(401, description="Invalid admin credentials.")

    return standardized_response(
        data={"access_token": access_token}, 
        message="Admin login successful."
    )
