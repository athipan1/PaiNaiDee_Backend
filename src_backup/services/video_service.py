import os
from werkzeug.utils import secure_filename
from src.models import db, VideoPost, User


class VideoService:
    UPLOAD_FOLDER = "uploads/videos"
    ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "wmv", "flv", "webm", "mkv"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def allowed_file(filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in VideoService.ALLOWED_EXTENSIONS
        )

    @staticmethod
    def save_video_file(file):
        """Save video file and return the file path"""
        if not file:
            return None, "No file provided"

        if not VideoService.allowed_file(file.filename):
            return None, "Invalid file type. Only video files are allowed."

        # Create upload directory if it doesn't exist
        os.makedirs(VideoService.UPLOAD_FOLDER, exist_ok=True)

        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            return None, "Invalid filename"

        # Generate unique filename to avoid conflicts
        base_name, ext = os.path.splitext(filename)
        counter = 1
        unique_filename = filename
        while os.path.exists(os.path.join(VideoService.UPLOAD_FOLDER, unique_filename)):
            unique_filename = f"{base_name}_{counter}{ext}"
            counter += 1

        file_path = os.path.join(VideoService.UPLOAD_FOLDER, unique_filename)
        
        try:
            file.save(file_path)
            return f"/{file_path}", None
        except Exception as e:
            return None, f"Error saving file: {str(e)}"

    @staticmethod
    def create_video_post(user_id, caption, video_file):
        """Create a new video post"""
        # Validate user exists
        user = db.session.get(User, user_id)
        if not user:
            return None, "User not found"

        # Save video file
        video_url, error = VideoService.save_video_file(video_file)
        if error:
            return None, error

        # Generate title from filename or caption
        title = caption if caption else "Untitled Video"
        if hasattr(video_file, 'filename') and video_file.filename:
            # Remove extension and use as title if no caption
            base_name = os.path.splitext(video_file.filename)[0]
            if not caption:
                title = base_name.replace('_', ' ').replace('-', ' ').title()

        # Create video post record
        video_post = VideoPost(
            user_id=user_id,
            title=title,
            caption=caption,
            video_url=video_url
        )

        try:
            db.session.add(video_post)
            db.session.commit()
            return video_post, "Video uploaded successfully"
        except Exception as e:
            db.session.rollback()
            # Clean up uploaded file if database save fails
            try:
                if video_url and os.path.exists(video_url[1:]):  # Remove leading slash
                    os.remove(video_url[1:])
            except:
                pass
            return None, f"Error saving video post: {str(e)}"

    @staticmethod
    def get_all_videos():
        """Get all video posts ordered by creation date (newest first)"""
        return (
            VideoPost.query
            .join(User)
            .order_by(VideoPost.created_at.desc())
            .all()
        )