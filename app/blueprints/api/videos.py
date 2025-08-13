from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_current_user
from marshmallow import ValidationError
from ...services.video_service import VideoService
from ...schemas.video import VideoUploadSchema, VideoListSchema
from ...utils.response import standardized_response

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


@videos_bp.route("/videos", methods=["GET"])
def get_videos():
    """Get all videos for explore feed"""
    videos = VideoService.get_all_videos()
    
    # Serialize videos using schema
    schema = VideoListSchema(many=True)
    videos_data = schema.dump([video.to_dict() for video in videos])
    
    return standardized_response(
        data=videos_data,
        message="Videos retrieved successfully"
    )