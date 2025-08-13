import os
import tempfile
import pytest
from werkzeug.security import generate_password_hash
from app.app import create_app
from app.models import db, User, VideoPost
from app.services.video_service import VideoService
from werkzeug.datastructures import FileStorage


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        hashed_password = generate_password_hash("testpass")
        user = User(username="testuser", password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def mock_video_file():
    """Create a mock video file for testing."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"fake video content")
        temp_file = f.name
    
    # Create FileStorage object
    with open(temp_file, "rb") as f:
        file_storage = FileStorage(
            stream=f,
            filename="test_video.mp4",
            content_type="video/mp4"
        )
        yield file_storage
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)


class TestVideoService:
    def test_allowed_file_valid_extensions(self):
        """Test allowed_file method with valid video extensions."""
        valid_files = [
            "video.mp4",
            "movie.avi", 
            "clip.mov",
            "test.wmv",
            "sample.flv",
            "video.webm",
            "movie.mkv"
        ]
        
        for filename in valid_files:
            assert VideoService.allowed_file(filename) is True

    def test_allowed_file_invalid_extensions(self):
        """Test allowed_file method with invalid extensions."""
        invalid_files = [
            "image.jpg",
            "document.pdf",
            "audio.mp3",
            "text.txt",
            "video"  # no extension
        ]
        
        for filename in invalid_files:
            assert VideoService.allowed_file(filename) is False

    def test_create_video_post_success(self, app):
        """Test successful video post creation."""
        with app.app_context():
            # Create a user directly in this context
            hashed_password = generate_password_hash("testpass")
            user = User(username="testuser2", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            # Create a temporary video file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(b"fake video content")
                temp_file = f.name
            
            try:
                # Create FileStorage object
                with open(temp_file, "rb") as f:
                    file_storage = FileStorage(
                        stream=f,
                        filename="test_video.mp4",
                        content_type="video/mp4"
                    )
                    
                    video_post, message = VideoService.create_video_post(
                        user.id,
                        "Test caption",
                        file_storage
                    )
                
                assert video_post is not None
                assert message == "Video uploaded successfully"
                assert video_post.user_id == user.id
                assert video_post.caption == "Test caption"
                assert video_post.video_url is not None
                
                # Verify video was saved to database
                saved_video = VideoPost.query.filter_by(id=video_post.id).first()
                assert saved_video is not None
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                # Clean up uploaded file
                if 'video_post' in locals() and video_post and video_post.video_url:
                    uploaded_path = video_post.video_url[1:]  # Remove leading slash
                    if os.path.exists(uploaded_path):
                        os.unlink(uploaded_path)

    def test_create_video_post_invalid_user(self, app):
        """Test video post creation with invalid user."""
        with app.app_context():
            # Create a temporary video file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(b"fake video content")
                temp_file = f.name
            
            try:
                with open(temp_file, "rb") as f:
                    file_storage = FileStorage(
                        stream=f,
                        filename="test_video.mp4",
                        content_type="video/mp4"
                    )
                    
                    video_post, message = VideoService.create_video_post(
                        999,  # Non-existent user ID
                        "Test caption",
                        file_storage
                    )
                
                assert video_post is None
                assert message == "User not found"
                
            finally:
                os.unlink(temp_file)

    def test_create_video_post_invalid_file(self, app):
        """Test video post creation with invalid file type."""
        with app.app_context():
            # Create a user directly in this context
            hashed_password = generate_password_hash("testpass")
            user = User(username="testuser3", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            # Create a temporary text file
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                f.write(b"not a video")
                temp_file = f.name
            
            try:
                with open(temp_file, "rb") as f:
                    file_storage = FileStorage(
                        stream=f,
                        filename="test_file.txt",
                        content_type="text/plain"
                    )
                    
                    video_post, message = VideoService.create_video_post(
                        user.id,
                        "Test caption",
                        file_storage
                    )
                
                assert video_post is None
                assert "Invalid file type" in message
                
            finally:
                os.unlink(temp_file)

    def test_get_all_videos(self, app):
        """Test getting all videos."""
        with app.app_context():
            # Create a user directly in this context
            hashed_password = generate_password_hash("testpass")
            user = User(username="testuser2", password=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            # Create test video posts
            video1 = VideoPost(
                user_id=user.id,
                title="First Video Title",
                caption="First video",
                video_url="/uploads/videos/video1.mp4"
            )
            video2 = VideoPost(
                user_id=user.id,
                title="Second Video Title", 
                caption="Second video", 
                video_url="/uploads/videos/video2.mp4"
            )
            
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
            
            videos = VideoService.get_all_videos()
            
            assert len(videos) == 2
            # Should be ordered by creation date desc (newest first)
            assert videos[0].caption == "Second video"
            assert videos[1].caption == "First video"