import os
import uuid
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


class StorageService:
    """
    Cloud storage service for handling video and thumbnail uploads.
    Currently implemented as local file storage, but can be extended
    to support AWS S3, Google Cloud Storage, etc.
    """
    
    VIDEO_UPLOAD_FOLDER = "uploads/videos"
    THUMBNAIL_UPLOAD_FOLDER = "uploads/thumbnails"
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "wmv", "flv", "webm", "mkv"}
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_THUMBNAIL_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def allowed_video_file(filename: str) -> bool:
        """Check if the video file extension is allowed"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in StorageService.ALLOWED_VIDEO_EXTENSIONS
        )

    @staticmethod
    def allowed_image_file(filename: str) -> bool:
        """Check if the image file extension is allowed"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in StorageService.ALLOWED_IMAGE_EXTENSIONS
        )

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename using UUID to avoid conflicts"""
        if not original_filename:
            return f"{uuid.uuid4()}.mp4"
        
        filename = secure_filename(original_filename)
        name, ext = os.path.splitext(filename)
        unique_id = str(uuid.uuid4())
        return f"{name}_{unique_id}{ext}"

    @staticmethod
    def save_video_file(file: FileStorage) -> Tuple[Optional[str], Optional[str]]:
        """
        Save video file to storage and return the URL
        Returns: (video_url, error_message)
        """
        if not file:
            return None, "No file provided"

        if not StorageService.allowed_video_file(file.filename):
            return None, "Invalid file type. Only video files are allowed."

        # Create upload directory if it doesn't exist
        os.makedirs(StorageService.VIDEO_UPLOAD_FOLDER, exist_ok=True)

        # Generate unique filename
        unique_filename = StorageService.generate_unique_filename(file.filename)
        file_path = os.path.join(StorageService.VIDEO_UPLOAD_FOLDER, unique_filename)
        
        try:
            file.save(file_path)
            # Return relative URL path
            return f"/{file_path}", None
        except Exception as e:
            return None, f"Error saving video file: {str(e)}"

    @staticmethod
    def save_thumbnail_file(file: FileStorage) -> Tuple[Optional[str], Optional[str]]:
        """
        Save thumbnail file to storage and return the URL
        Returns: (thumbnail_url, error_message)
        """
        if not file:
            return None, "No thumbnail file provided"

        if not StorageService.allowed_image_file(file.filename):
            return None, "Invalid file type. Only image files are allowed for thumbnails."

        # Create upload directory if it doesn't exist
        os.makedirs(StorageService.THUMBNAIL_UPLOAD_FOLDER, exist_ok=True)

        # Generate unique filename
        unique_filename = StorageService.generate_unique_filename(file.filename)
        file_path = os.path.join(StorageService.THUMBNAIL_UPLOAD_FOLDER, unique_filename)
        
        try:
            file.save(file_path)
            # Return relative URL path
            return f"/{file_path}", None
        except Exception as e:
            return None, f"Error saving thumbnail file: {str(e)}"

    @staticmethod
    def delete_file(file_url: str) -> bool:
        """
        Delete a file from storage
        Returns: True if successful, False otherwise
        """
        try:
            if file_url and file_url.startswith('/'):
                file_path = file_url[1:]  # Remove leading slash
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_file_size(file: FileStorage) -> int:
        """Get file size in bytes"""
        try:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)  # Reset file pointer
            return size
        except Exception:
            return 0

    # Future: AWS S3 implementation
    @staticmethod
    def upload_to_s3(file: FileStorage, bucket: str, key: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Upload file to AWS S3 (placeholder for future implementation)
        Returns: (s3_url, error_message)
        """
        # TODO: Implement S3 upload using boto3
        # This would replace the local file storage for production use
        pass

    # Future: Google Cloud Storage implementation
    @staticmethod
    def upload_to_gcs(file: FileStorage, bucket: str, blob_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Upload file to Google Cloud Storage (placeholder for future implementation)
        Returns: (gcs_url, error_message)
        """
        # TODO: Implement GCS upload using google-cloud-storage
        pass