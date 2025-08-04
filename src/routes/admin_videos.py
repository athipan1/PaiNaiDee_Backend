from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_current_user
from marshmallow import ValidationError
from src.services.video_service import VideoService
from src.schemas.video import AdminVideoUploadSchema, VideoListSchema
from src.utils.response import standardized_response

admin_videos_bp = Blueprint("admin_videos", __name__)


def require_admin():
    """Decorator to ensure only admin users can access the route"""
    current_user = get_current_user()
    if not current_user:
        abort(401, description="Authentication required")
    
    if not current_user.is_admin:
        abort(403, description="Admin access required")
    
    return current_user


@admin_videos_bp.route("/admin/videos/upload", methods=["POST"])
@jwt_required()
def upload_video():
    """Upload a new video (Admin only)"""
    current_admin = require_admin()

    # Get form data
    title = request.form.get("title", "")
    description = request.form.get("description", "")
    caption = request.form.get("caption", "")
    
    # Validate form data using schema
    try:
        validated_data = AdminVideoUploadSchema().load({
            "title": title,
            "description": description,
            "caption": caption
        })
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

    # Get optional thumbnail file
    thumbnail_file = request.files.get("thumbnail")

    # Create video post
    video_post, message = VideoService.create_video_post(
        current_admin.id, 
        validated_data["title"],
        validated_data.get("description", ""),
        validated_data.get("caption", ""),
        video_file,
        thumbnail_file
    )

    if not video_post:
        return standardized_response(message=message, success=False, status_code=400)

    return standardized_response(
        data=video_post.to_dict(),
        message=message,
        status_code=201
    )


@admin_videos_bp.route("/admin/videos", methods=["GET"])
@jwt_required()
def get_admin_videos():
    """Get all videos for the current admin (RLS - only their own videos)"""
    current_admin = require_admin()
    
    videos = VideoService.get_admin_videos(current_admin.id)
    
    # Serialize videos using schema
    schema = VideoListSchema(many=True)
    videos_data = schema.dump([video.to_dict() for video in videos])
    
    return standardized_response(
        data=videos_data,
        message=f"Retrieved {len(videos)} videos"
    )


@admin_videos_bp.route("/admin/videos/<int:video_id>", methods=["GET"])
@jwt_required()
def get_video_detail(video_id):
    """Get video details (RLS - admin can only see their own videos)"""
    current_admin = require_admin()
    
    video = VideoService.get_video_by_id(video_id, current_admin.id)
    
    if not video:
        return standardized_response(
            message="Video not found or access denied", 
            success=False, 
            status_code=404
        )
    
    return standardized_response(
        data=video.to_dict(),
        message="Video details retrieved successfully"
    )


@admin_videos_bp.route("/admin/videos/<int:video_id>", methods=["PUT"])
@jwt_required()
def update_video(video_id):
    """Update video details (RLS - admin can only update their own videos)"""
    current_admin = require_admin()
    
    data = request.get_json()
    if not data:
        return standardized_response(
            message="No data provided", success=False, status_code=400
        )
    
    # Validate data
    try:
        validated_data = AdminVideoUploadSchema().load(data)
    except ValidationError as err:
        return standardized_response(data=err.messages, success=False, status_code=400)
    
    video_post, message = VideoService.update_video_post(
        video_id,
        current_admin.id,
        title=validated_data.get("title"),
        description=validated_data.get("description"),
        caption=validated_data.get("caption")
    )
    
    if not video_post:
        return standardized_response(message=message, success=False, status_code=404)
    
    return standardized_response(
        data=video_post.to_dict(),
        message=message
    )


@admin_videos_bp.route("/admin/videos/<int:video_id>", methods=["DELETE"])
@jwt_required()
def delete_video(video_id):
    """Delete a video (RLS - admin can only delete their own videos)"""
    current_admin = require_admin()
    
    success, message = VideoService.delete_video_post(video_id, current_admin.id)
    
    if not success:
        return standardized_response(message=message, success=False, status_code=404)
    
    return standardized_response(message=message)


@admin_videos_bp.route("/admin/videos/stats", methods=["GET"])
@jwt_required()
def get_video_stats():
    """Get video statistics for the current admin"""
    current_admin = require_admin()
    
    videos = VideoService.get_admin_videos(current_admin.id)
    
    # Calculate statistics
    total_videos = len(videos)
    total_size = sum(video.file_size or 0 for video in videos)
    total_duration = sum(video.duration or 0 for video in videos)
    
    stats = {
        "total_videos": total_videos,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "total_duration_seconds": total_duration,
        "total_duration_minutes": round(total_duration / 60, 2),
        "average_size_mb": round(total_size / (1024 * 1024) / total_videos, 2) if total_videos > 0 else 0,
        "average_duration_minutes": round(total_duration / 60 / total_videos, 2) if total_videos > 0 else 0
    }
    
    return standardized_response(
        data=stats,
        message="Video statistics retrieved successfully"
    )