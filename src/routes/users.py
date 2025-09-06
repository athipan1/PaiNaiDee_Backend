from flask import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.user_service import UserService
from src.utils.response import standardized_response

users_bp = Blueprint("users", __name__)


@users_bp.route("/users/<int:user_id>/follow", methods=["POST"])
@jwt_required()
def toggle_follow_user(user_id):
    """
    Follow or unfollow a user.
    This endpoint acts as a toggle.
    """
    current_user_id = get_jwt_identity()

    # It's necessary to convert the identity from the JWT (which is a string) to an integer
    try:
        current_user_id = int(current_user_id)
    except ValueError:
        abort(400, description="Invalid user identity in token.")

    # Check if the user is trying to follow/unfollow themselves
    if current_user_id == user_id:
        return standardized_response(
            success=False,
            message="You cannot follow or unfollow yourself.",
            status_code=400
        )

    # Check if the current user is already following the target user
    is_currently_following = UserService.is_following(
        follower_id=current_user_id,
        followed_id=user_id
    )

    if is_currently_following:
        # If already following, unfollow the user
        success, message = UserService.unfollow_user(
            follower_id=current_user_id,
            followed_id=user_id
        )
        action = "unfollowed"
    else:
        # If not following, follow the user
        success, message = UserService.follow_user(
            follower_id=current_user_id,
            followed_id=user_id
        )
        action = "followed"

    if not success:
        # The service layer provides descriptive error messages
        abort(404, description=message)

    return standardized_response(
        data={"action": action, "target_user_id": user_id},
        message=message
    )
