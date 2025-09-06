import os
import tempfile
import pytest
from werkzeug.security import generate_password_hash
from src.app import create_app
from src.models import db, User, VideoPost


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


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
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    token = response.get_json()["data"]["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_video_file():
    """Create a sample video file for testing."""
    # Create a temporary file that simulates a video
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"fake video content for testing")
        return f.name


class TestVideoRoutes:
    def test_upload_video_success(self, client, auth_headers, sample_video_file):
        """Test successful video upload."""
        with open(sample_video_file, "rb") as f:
            response = client.post(
                "/api/videos/upload",
                data={
                    "caption": "Test video caption",
                    "video": (f, "test_video.mp4")
                },
                headers=auth_headers,
                content_type="multipart/form-data"
            )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["message"] == "Video uploaded successfully"
        assert "id" in data["data"]
        assert data["data"]["caption"] == "Test video caption"
        assert data["data"]["username"] == "testuser"
        
        # Clean up
        os.unlink(sample_video_file)

    def test_upload_video_unauthorized(self, client, sample_video_file):
        """Test video upload without authentication."""
        with open(sample_video_file, "rb") as f:
            response = client.post(
                "/api/videos/upload",
                data={
                    "caption": "Test video caption",
                    "video": (f, "test_video.mp4")
                },
                content_type="multipart/form-data"
            )
        
        assert response.status_code == 401
        
        # Clean up
        os.unlink(sample_video_file)

    def test_upload_video_no_file(self, client, auth_headers):
        """Test video upload with no file."""
        response = client.post(
            "/api/videos/upload",
            data={"caption": "Test video caption"},
            headers=auth_headers,
            content_type="multipart/form-data"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "No video file provided" in data["message"]

    def test_upload_video_invalid_file_type(self, client, auth_headers):
        """Test video upload with invalid file type."""
        # Create a fake text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a video file")
            temp_file = f.name

        try:
            with open(temp_file, "rb") as f:
                response = client.post(
                    "/api/videos/upload",
                    data={
                        "caption": "Test video caption",
                        "video": (f, "test_file.txt")
                    },
                    headers=auth_headers,
                    content_type="multipart/form-data"
                )
            
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "Invalid file type" in data["message"]
        finally:
            os.unlink(temp_file)

    def test_upload_video_caption_too_long(self, client, auth_headers, sample_video_file):
        """Test video upload with caption that's too long."""
        long_caption = "x" * 501  # Over 500 character limit
        
        with open(sample_video_file, "rb") as f:
            response = client.post(
                "/api/videos/upload",
                data={
                    "caption": long_caption,
                    "video": (f, "test_video.mp4")
                },
                headers=auth_headers,
                content_type="multipart/form-data"
            )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        
        # Clean up
        os.unlink(sample_video_file)

    def test_get_videos_empty(self, client):
        """Test getting videos when no videos exist."""
        response = client.get("/api/explore/videos")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == []

    def test_get_videos_with_data(self, client, app):
        """Test getting videos when videos exist."""
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

        response = client.get("/api/explore/videos")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        
        # Check that videos are ordered by creation date (newest first)
        assert data["data"][0]["caption"] == "Second video"
        assert data["data"][1]["caption"] == "First video"