import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.schemas.engagement import (
    PostCommentResponse, PostEngagementResponse, EngagementActionResponse
)
from datetime import datetime


@pytest.fixture
def client():
    """Create a test client for FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_engagement_response():
    """Create a mock engagement action response"""
    return EngagementActionResponse(
        success=True,
        message="Post liked successfully",
        like_count=6
    )


@pytest.fixture
def mock_comment_response():
    """Create a mock comment response"""
    return PostCommentResponse(
        id="test-comment-id",
        post_id="test-post-id",
        user_id="test-user-id",
        content="This is a test comment",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_post_engagement_response(mock_comment_response):
    """Create a mock post engagement response"""
    return PostEngagementResponse(
        post_id="test-post-id",
        like_count=10,
        comment_count=5,
        user_liked=True,
        recent_comments=[mock_comment_response]
    )


from app.auth.security import get_current_user, get_optional_current_user
from src.models import User

class TestEngagementAPI:
    """Test cases for Engagement API endpoints"""

    @pytest.fixture(autouse=True)
    def override_auth_dependency(self):
        """Fixture to override authentication dependency for all tests in this class."""
        mock_user = User(id=1, username="testuser")

        def mock_get_current_user():
            return mock_user

        def mock_get_optional_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user
        app.dependency_overrides[get_optional_current_user] = mock_get_optional_current_user
        yield
        app.dependency_overrides.clear()

    @patch('app.services.engagement_service.engagement_service.like_post')
    def test_like_post_success(self, mock_like_post, client, mock_engagement_response):
        """Test successful post liking"""
        mock_like_post.return_value = mock_engagement_response
        
        response = client.post("/api/posts/test-post-id/like")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Post liked successfully"
        assert data["like_count"] == 6

    @patch('app.services.engagement_service.engagement_service.like_post')
    def test_like_post_not_found(self, mock_like_post, client):
        """Test liking non-existent post"""
        mock_like_post.return_value = EngagementActionResponse(
            success=False,
            message="Post not found"
        )
        
        response = client.post("/api/posts/non-existent-id/like")
        
        assert response.status_code == 404
        data = response.json()
        assert "Post not found" in data["detail"]

    @patch('app.services.engagement_service.engagement_service.like_post')
    def test_like_post_invalid_id(self, mock_like_post, client):
        """Test liking post with invalid ID format"""
        mock_like_post.return_value = EngagementActionResponse(
            success=False,
            message="Invalid post ID format"
        )
        
        response = client.post("/api/posts/invalid-id/like")
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid post ID format" in data["detail"]

    @patch('app.services.engagement_service.engagement_service.comment_on_post')
    def test_create_comment_success(self, mock_comment_on_post, client, mock_comment_response):
        """Test successful comment creation"""
        mock_comment_on_post.return_value = mock_comment_response
        
        response = client.post(
            "/api/posts/test-post-id/comments",
            json={"content": "This is a test comment"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-comment-id"
        assert data["content"] == "This is a test comment"
        assert data["post_id"] == "test-post-id"

    @patch('app.services.engagement_service.engagement_service.comment_on_post')
    def test_create_comment_post_not_found(self, mock_comment_on_post, client):
        """Test commenting on non-existent post"""
        mock_comment_on_post.side_effect = ValueError("Post not found")
        
        response = client.post(
            "/api/posts/non-existent-id/comments",
            json={"content": "This is a test comment"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Post not found" in data["detail"]

    @patch('app.services.engagement_service.engagement_service.update_comment')
    def test_update_comment_success(self, mock_update_comment, client, mock_comment_response):
        """Test successful comment update"""
        mock_update_comment.return_value = mock_comment_response
        
        response = client.put(
            "/api/comments/test-comment-id",
            json={"content": "Updated comment content"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-comment-id"
        assert data["content"] == "This is a test comment"

    @patch('app.services.engagement_service.engagement_service.update_comment')
    def test_update_comment_permission_denied(self, mock_update_comment, client):
        """Test updating comment by non-owner"""
        mock_update_comment.side_effect = PermissionError("You can only edit your own comments")
        
        response = client.put(
            "/api/comments/test-comment-id",
            json={"content": "Updated comment content"}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "only edit your own comments" in data["detail"]

    @patch('app.services.engagement_service.engagement_service.delete_comment')
    def test_delete_comment_success(self, mock_delete_comment, client):
        """Test successful comment deletion"""
        mock_delete_comment.return_value = EngagementActionResponse(
            success=True,
            message="Comment deleted successfully",
            comment_count=4
        )
        
        response = client.delete("/api/comments/test-comment-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Comment deleted successfully"
        assert data["comment_count"] == 4

    @patch('app.services.engagement_service.engagement_service.delete_comment')
    def test_delete_comment_permission_denied(self, mock_delete_comment, client):
        """Test deleting comment by non-owner"""
        mock_delete_comment.return_value = EngagementActionResponse(
            success=False,
            message="You can only delete your own comments"
        )
        
        response = client.delete("/api/comments/test-comment-id")
        
        assert response.status_code == 403
        data = response.json()
        assert "only delete your own comments" in data["detail"]

    @patch('app.services.engagement_service.engagement_service.get_post_engagement')
    def test_get_post_engagement_success(self, mock_get_engagement, client, mock_post_engagement_response):
        """Test successful post engagement retrieval"""
        mock_get_engagement.return_value = mock_post_engagement_response
        
        response = client.get("/api/posts/test-post-id/engagement")
        
        assert response.status_code == 200
        data = response.json()
        assert data["post_id"] == "test-post-id"
        assert data["like_count"] == 10
        assert data["comment_count"] == 5
        assert data["user_liked"] is True
        assert len(data["recent_comments"]) == 1

    @patch('app.services.engagement_service.engagement_service.get_post_engagement')
    def test_get_post_engagement_with_limit(self, mock_get_engagement, client, mock_post_engagement_response):
        """Test post engagement retrieval with comment limit"""
        mock_get_engagement.return_value = mock_post_engagement_response
        
        response = client.get("/api/posts/test-post-id/engagement?limit_comments=3")
        
        assert response.status_code == 200
        # Verify the service was called with correct limit
        mock_get_engagement.assert_called_once()

    @patch('app.services.engagement_service.engagement_service.get_post_engagement')
    def test_get_post_engagement_not_found(self, mock_get_engagement, client):
        """Test engagement retrieval for non-existent post"""
        mock_get_engagement.return_value = None
        
        response = client.get("/api/posts/non-existent-id/engagement")
        
        assert response.status_code == 404
        data = response.json()
        assert "Post not found" in data["detail"]

    @patch('app.services.engagement_service.engagement_service.like_post')
    def test_like_post_service_error(self, mock_like_post, client):
        """Test error handling when like service fails"""
        mock_like_post.side_effect = Exception("Database error")
        
        response = client.post("/api/posts/test-post-id/like")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to like post" in data["detail"]