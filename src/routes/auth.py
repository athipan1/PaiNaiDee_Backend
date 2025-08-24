from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.auth_service import AuthService
from src.utils.response import standardized_response
from src.schemas.auth import RegisterSchema, LoginSchema
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
    password = validated_data["password"]
    email = validated_data.get("email")

    user, message = AuthService.register_user(username, password, email)

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

    username = validated_data["username"]
    password = validated_data["password"]

    access_token, refresh_token = AuthService.login_user(username, password)

    if not access_token:
        abort(401, description="Invalid credentials.")

    return standardized_response(
        data={"access_token": access_token, "refresh_token": refresh_token},
        message="Login successful.",
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_identity = get_jwt_identity()
    new_access_token = AuthService.refresh_token(identity=current_user_identity)
    return standardized_response(
        data={"access_token": new_access_token},
        message="Access token has been refreshed.",
    )
