import os
import tempfile
import json
import pytest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import FileStorage
from src.app import create_app
from src.models import db, User, VideoPost


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def admin_user_data():
    """Return admin user data for creating users in tests."""
    return {
        "username": "admin",
        "email": "admin@painaidee.com",
        "password": "adminpass123",
        "is_admin": True
    }


@pytest.fixture
def regular_user_data():
    """Return regular user data for creating users in tests."""
    return {
        "username": "regularuser",
        "email": "user@painaidee.com", 
        "password": "userpass123",
        "is_admin": False
    }


def create_admin_user(app, admin_user_data):
    """Helper function to create admin user within app context."""
    with app.app_context():
        hashed_password = generate_password_hash(admin_user_data["password"])
        admin = User(
            username=admin_user_data["username"],
            email=admin_user_data["email"],
            password=hashed_password,
            is_admin=admin_user_data["is_admin"]
        )
        db.session.add(admin)
        db.session.commit()
        return admin.id


def create_regular_user(app, regular_user_data):
    """Helper function to create regular user within app context."""
    with app.app_context():
        hashed_password = generate_password_hash(regular_user_data["password"])
        user = User(
            username=regular_user_data["username"],
            email=regular_user_data["email"],
            password=hashed_password,
            is_admin=regular_user_data["is_admin"]
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def admin_token(app, admin_user_data):
    """Create access token for admin user."""
    admin_id = create_admin_user(app, admin_user_data)
    with app.app_context():
        access_token = create_access_token(identity=str(admin_id))
        return access_token


@pytest.fixture
def regular_token(app, regular_user_data):
    """Create access token for regular user."""
    user_id = create_regular_user(app, regular_user_data)
    with app.app_context():
        access_token = create_access_token(identity=str(user_id))
        return access_token


@pytest.fixture
def admin_headers(admin_token):
    """Create authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def regular_headers(regular_token):
    """Create authorization headers for regular user."""
    return {"Authorization": f"Bearer {regular_token}"}


@pytest.fixture
def sample_video_file():
    """Create a mock video file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"fake video content for testing")
        temp_file = f.name
    
    yield temp_file
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def sample_thumbnail_file():
    """Create a mock thumbnail file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"fake image content for testing")
        temp_file = f.name
    
    yield temp_file
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)


class TestAdminAuthentication:
    """Test admin authentication endpoints."""
    
    def test_admin_register_success(self, client):
        """Test successful admin registration."""
        data = {
            "username": "newadmin",
            "email": "newadmin@painaidee.com",
            "password": "securepass123"
        }
        
        response = client.post("/api/auth/admin/register", json=data)
        assert response.status_code == 201
        
        json_data = response.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["username"] == "newadmin"
        assert json_data["data"]["email"] == "newadmin@painaidee.com"
        assert "admin_id" in json_data["data"]
    
    def test_admin_register_duplicate_email(self, client, app, admin_user_data):
        """Test admin registration with duplicate email."""
        # Create the admin user first
        create_admin_user(app, admin_user_data)
        
        data = {
            "username": "anotheradmin",
            "email": "admin@painaidee.com",  # Same as existing admin
            "password": "securepass123"
        }
        
        response = client.post("/api/auth/admin/register", json=data)
        assert response.status_code == 409
    
    def test_admin_login_success(self, client, app, admin_user_data):
        """Test successful admin login."""
        # Create the admin user first
        create_admin_user(app, admin_user_data)
        
        data = {
            "email": "admin@painaidee.com",
            "password": "adminpass123"
        }
        
        response = client.post("/api/auth/admin/login", json=data)
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["success"] is True
        assert "access_token" in json_data["data"]
    
    def test_admin_login_invalid_credentials(self, client, app, admin_user_data):
        """Test admin login with invalid credentials."""
        # Create the admin user first
        create_admin_user(app, admin_user_data)
        
        data = {
            "email": "admin@painaidee.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/admin/login", json=data)
        assert response.status_code == 401


class TestAdminVideoManagement:
    """Test admin video management endpoints."""
    
    def test_upload_video_success(self, client, admin_headers, sample_video_file, sample_thumbnail_file):
        """Test successful video upload by admin."""
        with open(sample_video_file, "rb") as video_f, open(sample_thumbnail_file, "rb") as thumb_f:
            data = {
                "title": "Test Video",
                "description": "This is a test video",
                "caption": "Test caption"
            }
            files = {
                "video": (video_f, "test_video.mp4", "video/mp4"),
                "thumbnail": (thumb_f, "test_thumb.jpg", "image/jpeg")
            }
            
            response = client.post(
                "/api/admin/videos/upload",
                data={**data, **files},
                headers=admin_headers
            )
            
            assert response.status_code == 201
            json_data = response.get_json()
            assert json_data["success"] is True
            assert json_data["data"]["title"] == "Test Video"
            assert json_data["data"]["description"] == "This is a test video"
            assert json_data["data"]["caption"] == "Test caption"
            assert json_data["data"]["video_url"] is not None
            assert json_data["data"]["thumbnail_url"] is not None
    
    def test_upload_video_regular_user_forbidden(self, client, regular_headers, sample_video_file):
        """Test video upload forbidden for regular users."""
        with open(sample_video_file, "rb") as video_f:
            data = {
                "title": "Test Video",
                "description": "This is a test video"
            }
            files = {
                "video": (video_f, "test_video.mp4", "video/mp4")
            }
            
            response = client.post(
                "/api/admin/videos/upload",
                data={**data, **files},
                headers=regular_headers
            )
            
            assert response.status_code == 403
    
    def test_upload_video_no_auth(self, client, sample_video_file):
        """Test video upload without authentication."""
        with open(sample_video_file, "rb") as video_f:
            data = {
                "title": "Test Video"
            }
            files = {
                "video": (video_f, "test_video.mp4", "video/mp4")
            }
            
            response = client.post(
                "/api/admin/videos/upload",
                data={**data, **files}
            )
            
            assert response.status_code == 401
    
    def test_upload_video_missing_title(self, client, admin_headers, sample_video_file):
        """Test video upload with missing required title."""
        with open(sample_video_file, "rb") as video_f:
            data = {
                "description": "This is a test video"
            }
            files = {
                "video": (video_f, "test_video.mp4", "video/mp4")
            }
            
            response = client.post(
                "/api/admin/videos/upload",
                data={**data, **files},
                headers=admin_headers
            )
            
            assert response.status_code == 400
    
    def test_upload_video_no_file(self, client, admin_headers):
        """Test video upload without video file."""
        data = {
            "title": "Test Video",
            "description": "This is a test video"
        }
        
        response = client.post(
            "/api/admin/videos/upload",
            data=data,
            headers=admin_headers
        )
        
        assert response.status_code == 400
    
    def test_get_admin_videos(self, app, client, admin_token, admin_user_data):
        """Test getting admin's own videos."""
        admin_id = create_admin_user(app, admin_user_data)
        
        with app.app_context():
            # Create test videos for this admin
            video1 = VideoPost(
                user_id=admin_id,
                title="Video 1",
                description="First video",
                caption="First caption",
                video_url="/uploads/videos/video1.mp4"
            )
            video2 = VideoPost(
                user_id=admin_id,
                title="Video 2", 
                description="Second video",
                caption="Second caption",
                video_url="/uploads/videos/video2.mp4"
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/videos", headers=headers)
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["success"] is True
        assert len(json_data["data"]) == 2
        assert json_data["data"][0]["title"] in ["Video 1", "Video 2"]
    
    def test_get_admin_videos_rls_enforcement(self, app, client, admin_user, admin_headers):
        """Test RLS: admin only sees their own videos."""
        with app.app_context():
            # Create another admin
            other_admin = User(
                username="otheradmin",
                email="other@painaidee.com",
                password=generate_password_hash("pass123"),
                is_admin=True
            )
            db.session.add(other_admin)
            db.session.commit()
            
            # Create videos for both admins
            video1 = VideoPost(
                user_id=admin_user.id,
                title="My Video",
                video_url="/uploads/videos/my_video.mp4"
            )
            video2 = VideoPost(
                user_id=other_admin.id,
                title="Other Video",
                video_url="/uploads/videos/other_video.mp4"
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        response = client.get("/api/admin/videos", headers=admin_headers)
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["success"] is True
        assert len(json_data["data"]) == 1
        assert json_data["data"][0]["title"] == "My Video"
    
    def test_get_video_detail(self, app, client, admin_user, admin_headers):
        """Test getting specific video details."""
        with app.app_context():
            video = VideoPost(
                user_id=admin_user.id,
                title="Test Video",
                description="Test description",
                caption="Test caption",
                video_url="/uploads/videos/test.mp4",
                thumbnail_url="/uploads/thumbnails/test.jpg"
            )
            db.session.add(video)
            db.session.commit()
            video_id = video.id
        
        response = client.get(f"/api/admin/videos/{video_id}", headers=admin_headers)
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["title"] == "Test Video"
        assert json_data["data"]["description"] == "Test description"
        assert json_data["data"]["thumbnail_url"] == "/uploads/thumbnails/test.jpg"
    
    def test_get_video_detail_not_found(self, client, admin_headers):
        """Test getting non-existent video."""
        response = client.get("/api/admin/videos/99999", headers=admin_headers)
        assert response.status_code == 404
    
    def test_update_video(self, app, client, admin_user, admin_headers):
        """Test updating video details."""
        with app.app_context():
            video = VideoPost(
                user_id=admin_user.id,
                title="Original Title",
                description="Original description",
                video_url="/uploads/videos/test.mp4"
            )
            db.session.add(video)
            db.session.commit()
            video_id = video.id
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "caption": "Updated caption"
        }
        
        response = client.put(
            f"/api/admin/videos/{video_id}",
            json=update_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["title"] == "Updated Title"
        assert json_data["data"]["description"] == "Updated description"
        assert json_data["data"]["caption"] == "Updated caption"
    
    def test_delete_video(self, app, client, admin_user, admin_headers):
        """Test deleting a video."""
        with app.app_context():
            video = VideoPost(
                user_id=admin_user.id,
                title="Video to Delete",
                video_url="/uploads/videos/delete_me.mp4"
            )
            db.session.add(video)
            db.session.commit()
            video_id = video.id
        
        response = client.delete(f"/api/admin/videos/{video_id}", headers=admin_headers)
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["success"] is True
        assert "deleted successfully" in json_data["message"]
        
        # Verify video is deleted from database
        with app.app_context():
            deleted_video = VideoPost.query.filter_by(id=video_id).first()
            assert deleted_video is None
    
    def test_get_video_stats(self, app, client, admin_user, admin_headers):
        """Test getting video statistics for admin."""
        with app.app_context():
            # Create test videos with different sizes
            video1 = VideoPost(
                user_id=admin_user.id,
                title="Video 1",
                video_url="/uploads/videos/video1.mp4",
                file_size=1024 * 1024,  # 1MB
                duration=60  # 60 seconds
            )
            video2 = VideoPost(
                user_id=admin_user.id,
                title="Video 2",
                video_url="/uploads/videos/video2.mp4",
                file_size=2 * 1024 * 1024,  # 2MB
                duration=120  # 120 seconds
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        response = client.get("/api/admin/videos/stats", headers=admin_headers)
        assert response.status_code == 200
        
        json_data = response.get_json()
        assert json_data["success"] is True
        
        stats = json_data["data"]
        assert stats["total_videos"] == 2
        assert stats["total_size_mb"] == 3.0  # 1MB + 2MB
        assert stats["total_duration_minutes"] == 3.0  # 60s + 120s = 180s = 3min
        assert stats["average_size_mb"] == 1.5  # 3MB / 2 videos
        assert stats["average_duration_minutes"] == 1.5  # 3min / 2 videos


class TestRowLevelSecurity:
    """Test Row-Level Security enforcement."""
    
    def test_admin_cannot_access_other_admin_videos(self, app, client):
        """Test that admins cannot access videos from other admins."""
        with app.app_context():
            # Create two admin users
            admin1 = User(
                username="admin1",
                email="admin1@painaidee.com",
                password=generate_password_hash("pass123"),
                is_admin=True
            )
            admin2 = User(
                username="admin2",
                email="admin2@painaidee.com",
                password=generate_password_hash("pass123"),
                is_admin=True
            )
            db.session.add(admin1)
            db.session.add(admin2)
            db.session.commit()
            
            # Create video for admin2
            video = VideoPost(
                user_id=admin2.id,
                title="Admin2's Video",
                video_url="/uploads/videos/admin2_video.mp4"
            )
            db.session.add(video)
            db.session.commit()
            video_id = video.id
            
            # Create auth headers for admin1
            admin1_token = create_access_token(identity=str(admin1.id))
            admin1_headers = {"Authorization": f"Bearer {admin1_token}"}
        
        # Admin1 tries to access Admin2's video
        response = client.get(f"/api/admin/videos/{video_id}", headers=admin1_headers)
        assert response.status_code == 404  # Should not be found due to RLS
        
        # Admin1 tries to delete Admin2's video
        response = client.delete(f"/api/admin/videos/{video_id}", headers=admin1_headers)
        assert response.status_code == 404  # Should not be found due to RLS