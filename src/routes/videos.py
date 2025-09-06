from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_current_user
from marshmallow import ValidationError
from src.services.video_service import VideoService
from src.schemas.video import VideoUploadSchema, VideoListSchema
from src.utils.response import standardized_response

videos_bp = Blueprint("videos", __name__)


@videos_bp.route("/videos/upload", methods=["POST"])
@jwt_required()
def upload_video():
    """Upload a new video"""
    current_user = get_current_user()
    if not current_user:
        abort(401, description="Authentication required")

    # Get caption from form data
    caption = request.form.get("caption", "")
    
    # Validate caption using schema
    try:
        validated_data = VideoUploadSchema().load({"caption": caption})
        caption = validated_data.get("caption", "")
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)

    # Get video file
    if "video" not in request.files:
        return standardized_response(
            message="No video file provided", success=False, status_code=400
        )

    video_file = request.files["video"]
    if video_file.filename == "":
        return standardized_response(
            message="No video file selected", success=False, status_code=400
        )

    # Create video post
    video_post, message = VideoService.create_video_post(
        current_user.id, caption, video_file
    )

    if not video_post:
        return standardized_response(message=message, success=False, status_code=400)

    return standardized_response(
        data=video_post.to_dict(),
        message=message,
        status_code=201
    )


@videos_bp.route("/explore/videos", methods=["GET"])
def get_explore_videos():
    """Get all videos for explore feed"""
    videos = VideoService.get_all_videos()
    
    # Serialize videos using schema
    schema = VideoListSchema(many=True)
    videos_data = schema.dump([video.to_dict() for video in videos])
    
    return standardized_response(
        data=videos_data,
        message="Videos retrieved successfully"
    )


@videos_bp.route("/videos/<videoId>/like", methods=["POST"])
@jwt_required()
def like_video(videoId):
    """Toggle like/unlike on a video."""
    # Dummy response for now
    return standardized_response(data={"liked": True, "likes_count": 1})


@videos_bp.route("/videos/<videoId>/comments", methods=["GET"])
def get_video_comments(videoId):
    """Fetch comments for a specific video."""
    # Dummy response for now
    comments = [
        {"id": 1, "user": "user1", "comment": "Great video!"},
        {"id": 2, "user": "user2", "comment": "Awesome content!"},
    ]
    return standardized_response(data=comments)


@videos_bp.route("/videos/<videoId>/comments", methods=["POST"])
@jwt_required()
def add_video_comment(videoId):
    """Add a new comment to a video."""
    # Dummy response for now
    data = request.get_json()
    comment_text = data.get("comment", "")
    new_comment = {"id": 3, "user": "current_user", "comment": comment_text}
    return standardized_response(data=new_comment, status_code=201)


@videos_bp.route("/videos/<videoId>/share", methods=["POST"])
@jwt_required()
def share_video(videoId):
    """Record a video share event."""
    # In a real application, this might increment a share counter
    # or log an analytics event. For now, it's just a placeholder.
    return standardized_response(
        data={"video_id": videoId, "shared": True},
        message="Video share event recorded successfully."
    )