from flask import Blueprint, request, abort
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

    user, message = AuthService.register_user(username, password)

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

    access_token = AuthService.login_user(username, password)

    if not access_token:
        abort(401, description="Invalid credentials.")

    return standardized_response(
        data={"access_token": access_token}, message="Login successful."
    )
