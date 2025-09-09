import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.schemas.posts import PostResponse, PostListResponse
from datetime import datetime


@pytest.fixture
def client():
    """Create a test client for FastAPI"""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_post_response():
    """Create a mock post response"""
    return PostResponse(
        id="test-post-id",
        user_id="test-user-id",
        caption="Test post caption",
        tags=["test", "post"],
        location_id=None,
        lat=None,
        lng=None,
        like_count=5,
        comment_count=3,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_post_list_response(mock_post_response):
    """Create a mock post list response"""
    return PostListResponse(
        posts=[mock_post_response],
        total_count=1,
        page=1,
        page_size=10,
        total_pages=1
    )


class TestPostsAPI:
    """Test cases for Posts API endpoints"""

    @patch('app.services.post_service.post_service.get_posts')
    def test_get_posts_success(self, mock_get_posts, client, mock_post_list_response):
        """Test successful retrieval of posts list"""
        # Mock the service method
        mock_get_posts.return_value = mock_post_list_response
        
        # Make request
        response = client.get("/api/posts")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total_count"] == 1
        assert len(data["posts"]) == 1
        assert data["posts"][0]["id"] == "test-post-id"

    @patch('app.services.post_service.post_service.get_posts')
    def test_get_posts_with_pagination(self, mock_get_posts, client, mock_post_list_response):
        """Test posts retrieval with pagination parameters"""
        mock_get_posts.return_value = mock_post_list_response
        
        # Make request with pagination
        response = client.get("/api/posts?page=2&page_size=5")
        
        assert response.status_code == 200
        # Verify the service was called with correct parameters
        mock_get_posts.assert_called_once()

    def test_get_posts_invalid_pagination(self, client):
        """Test posts retrieval with invalid pagination parameters"""
        # Test negative page number
        response = client.get("/api/posts?page=0")
        assert response.status_code == 422
        
        # Test page size too large
        response = client.get("/api/posts?page_size=100")
        assert response.status_code == 422

    @patch('app.services.post_service.post_service.get_post_by_id')
    def test_get_post_by_id_success(self, mock_get_post, client, mock_post_response):
        """Test successful retrieval of a specific post"""
        mock_get_post.return_value = mock_post_response
        
        response = client.get("/api/posts/test-post-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-post-id"
        assert data["caption"] == "Test post caption"
        assert data["like_count"] == 5
        assert data["comment_count"] == 3

    @patch('app.services.post_service.post_service.get_post_by_id')
    def test_get_post_by_id_not_found(self, mock_get_post, client):
        """Test retrieval of non-existent post"""
        mock_get_post.return_value = None
        
        response = client.get("/api/posts/non-existent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "Post not found" in data["message"]

    @patch('app.services.post_service.post_service.get_posts')
    def test_get_posts_service_error(self, mock_get_posts, client):
        """Test error handling when service fails"""
        mock_get_posts.side_effect = Exception("Database error")
        
        response = client.get("/api/posts")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "InternalServerError"
        assert data["message"] == "An unexpected internal error occurred."

    @patch('app.services.post_service.post_service.get_post_by_id')
    def test_get_post_by_id_service_error(self, mock_get_post, client):
        """Test error handling when service fails for specific post"""
        mock_get_post.side_effect = Exception("Database error")
        
        response = client.get("/api/posts/test-id")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "InternalServerError"
        assert data["message"] == "An unexpected internal error occurred."