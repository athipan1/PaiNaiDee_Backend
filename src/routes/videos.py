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


@videos_bp.route("/videos/<int:videoId>/like", methods=["POST"])
@jwt_required()
def like_video(videoId):
    """Toggle like/unlike on a video."""
    current_user = get_current_user()
    if not current_user:
        abort(401, description="Authentication required")

    result, message = VideoService.toggle_like(current_user.id, videoId)

    if result is None:
        return standardized_response(message=message, success=False, status_code=404)

    return standardized_response(data=result, message=message)


@videos_bp.route("/videos/<int:videoId>/comments", methods=["GET"])
def get_video_comments(videoId):
    """Fetch comments for a specific video."""
    comments, message = VideoService.get_comments(videoId)

    if not comments and message == "Video not found":
        return standardized_response(message=message, success=False, status_code=404)

    comments_data = [comment.to_dict() for comment in comments]
    return standardized_response(data=comments_data, message=message)


@videos_bp.route("/videos/<int:videoId>/comments", methods=["POST"])
@jwt_required()
def add_video_comment(videoId):
    """Add a new comment to a video."""
    current_user = get_current_user()
    if not current_user:
        abort(401, description="Authentication required")

    data = request.get_json()
    if not data or "text" not in data:
        return standardized_response(message="Comment text is required.", success=False, status_code=400)

    comment_text = data.get("text")

    new_comment, message = VideoService.add_comment(current_user.id, videoId, comment_text)

    if not new_comment:
        status_code = 404 if "not found" in message else 400
        return standardized_response(message=message, success=False, status_code=status_code)

    return standardized_response(data=new_comment.to_dict(), message=message, status_code=201)