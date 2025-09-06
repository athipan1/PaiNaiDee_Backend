import os
from werkzeug.utils import secure_filename
from src.models import db, VideoPost, User, Like, Comment


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
            except Exception:
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

    @staticmethod
    def get_video_by_id(video_id):
        return VideoPost.query.get(video_id)

    @staticmethod
    def toggle_like(user_id, video_id):
        video_post = VideoService.get_video_by_id(video_id)
        if not video_post:
            return None, "Video not found"

        like = Like.query.filter_by(user_id=user_id, video_post_id=video_id).first()

        if like:
            db.session.delete(like)
            db.session.commit()
            return {"liked": False, "likes_count": video_post.likes.count()}, "Video unliked successfully"
        else:
            new_like = Like(user_id=user_id, video_post_id=video_id)
            db.session.add(new_like)
            db.session.commit()
            return {"liked": True, "likes_count": video_post.likes.count()}, "Video liked successfully"

    @staticmethod
    def add_comment(user_id, video_id, content):
        video_post = VideoService.get_video_by_id(video_id)
        if not video_post:
            return None, "Video not found"

        new_comment = Comment(user_id=user_id, video_post_id=video_id, content=content)
        db.session.add(new_comment)
        db.session.commit()
        return new_comment, "Comment added successfully"

    @staticmethod
    def get_comments(video_id):
        video_post = VideoService.get_video_by_id(video_id)
        if not video_post:
            return None, "Video not found"

        comments = Comment.query.filter_by(video_post_id=video_id).order_by(Comment.created_at.asc()).all()
        return comments, "Comments retrieved successfully"

    @staticmethod
    def record_share(video_id):
        # Placeholder for share logic. In a real app, this might increment a counter.
        video_post = VideoService.get_video_by_id(video_id)
        if not video_post:
            return None, "Video not found"
        # For now, we just confirm the action happened.
        return {"shared": True, "video_id": video_id}, "Share recorded successfully"