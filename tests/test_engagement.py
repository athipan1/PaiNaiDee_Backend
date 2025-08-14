"""
Tests for post engagement functionality (likes and comments)
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.services.engagement_service import engagement_service
from app.schemas.engagement import PostCommentCreate, PostCommentUpdate
from app.db.models import Post, PostLike, PostComment


class TestEngagementService:
    """Test cases for EngagementService"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        mock_session = AsyncMock()
        return mock_session
    
    @pytest.fixture
    def sample_post(self):
        """Sample post for testing"""
        post = Post()
        post.id = uuid.uuid4()
        post.user_id = "test_user_123"
        post.caption = "Test post"
        post.like_count = 0
        post.comment_count = 0
        post.created_at = datetime.utcnow()
        post.updated_at = datetime.utcnow()
        return post
    
    @pytest.fixture
    def sample_comment(self):
        """Sample comment for testing"""
        comment = PostComment()
        comment.id = uuid.uuid4()
        comment.post_id = uuid.uuid4()
        comment.user_id = "test_user_123"
        comment.content = "Test comment"
        comment.created_at = datetime.utcnow()
        comment.updated_at = datetime.utcnow()
        return comment
    
    @pytest.mark.asyncio
    async def test_like_post_success(self, mock_db_session, sample_post):
        """Test successful post liking"""
        # Setup
        mock_db_session.execute = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        # Mock post query
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = sample_post
        
        # Mock like query (no existing like)
        like_result = MagicMock()
        like_result.scalar_one_or_none.return_value = None
        
        mock_db_session.execute.side_effect = [post_result, like_result]
        
        # Test
        result = await engagement_service.like_post(
            str(sample_post.id), 
            "test_user_456", 
            mock_db_session
        )
        
        # Assertions
        assert result.success is True
        assert result.message == "Post liked successfully"
        assert result.like_count == 1
        assert sample_post.like_count == 1
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unlike_post_success(self, mock_db_session, sample_post):
        """Test successful post unliking"""
        # Setup
        sample_post.like_count = 1
        existing_like = PostLike()
        existing_like.id = uuid.uuid4()
        existing_like.post_id = sample_post.id
        existing_like.user_id = "test_user_456"
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        # Mock post query
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = sample_post
        
        # Mock like query (existing like found)
        like_result = MagicMock()
        like_result.scalar_one_or_none.return_value = existing_like
        
        mock_db_session.execute.side_effect = [post_result, like_result]
        
        # Test
        result = await engagement_service.like_post(
            str(sample_post.id), 
            "test_user_456", 
            mock_db_session
        )
        
        # Assertions
        assert result.success is True
        assert result.message == "Post unliked successfully"
        assert result.like_count == 0
        assert sample_post.like_count == 0
        mock_db_session.delete.assert_called_once_with(existing_like)
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_like_post_not_found(self, mock_db_session):
        """Test liking non-existent post"""
        # Setup
        mock_db_session.execute = AsyncMock()
        
        # Mock post query (no post found)
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = post_result
        
        # Test
        result = await engagement_service.like_post(
            str(uuid.uuid4()), 
            "test_user_456", 
            mock_db_session
        )
        
        # Assertions
        assert result.success is False
        assert result.message == "Post not found"
    
    @pytest.mark.asyncio
    async def test_like_post_invalid_id(self, mock_db_session):
        """Test liking with invalid post ID"""
        # Test
        result = await engagement_service.like_post(
            "invalid-uuid", 
            "test_user_456", 
            mock_db_session
        )
        
        # Assertions
        assert result.success is False
        assert result.message == "Invalid post ID format"
    
    @pytest.mark.asyncio
    async def test_comment_on_post_success(self, mock_db_session, sample_post):
        """Test successful comment creation"""
        # Setup
        mock_db_session.execute = AsyncMock()
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Mock post query
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = sample_post
        mock_db_session.execute.return_value = post_result
        
        comment_data = PostCommentCreate(
            post_id=str(sample_post.id),
            content="Great post!"
        )
        
        # Test
        result = await engagement_service.comment_on_post(
            comment_data,
            "test_user_456",
            mock_db_session
        )
        
        # Assertions
        assert result.post_id == str(sample_post.id)
        assert result.user_id == "test_user_456"
        assert result.content == "Great post!"
        assert sample_post.comment_count == 1
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_comment_on_nonexistent_post(self, mock_db_session):
        """Test commenting on non-existent post"""
        # Setup
        mock_db_session.execute = AsyncMock()
        
        # Mock post query (no post found)
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = post_result
        
        comment_data = PostCommentCreate(
            post_id=str(uuid.uuid4()),
            content="Great post!"
        )
        
        # Test
        with pytest.raises(ValueError, match="Post not found"):
            await engagement_service.comment_on_post(
                comment_data,
                "test_user_456",
                mock_db_session
            )
    
    @pytest.mark.asyncio
    async def test_update_comment_success(self, mock_db_session, sample_comment):
        """Test successful comment update"""
        # Setup
        mock_db_session.execute = AsyncMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Mock comment query
        comment_result = MagicMock()
        comment_result.scalar_one_or_none.return_value = sample_comment
        mock_db_session.execute.return_value = comment_result
        
        comment_data = PostCommentUpdate(content="Updated comment text")
        
        # Test
        result = await engagement_service.update_comment(
            str(sample_comment.id),
            comment_data,
            sample_comment.user_id,
            mock_db_session
        )
        
        # Assertions
        assert result.content == "Updated comment text"
        assert sample_comment.content == "Updated comment text"
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_comment_permission_denied(self, mock_db_session, sample_comment):
        """Test updating comment by different user"""
        # Setup
        mock_db_session.execute = AsyncMock()
        
        # Mock comment query
        comment_result = MagicMock()
        comment_result.scalar_one_or_none.return_value = sample_comment
        mock_db_session.execute.return_value = comment_result
        
        comment_data = PostCommentUpdate(content="Updated comment text")
        
        # Test - different user trying to update
        with pytest.raises(PermissionError, match="You can only edit your own comments"):
            await engagement_service.update_comment(
                str(sample_comment.id),
                comment_data,
                "different_user_456",  # Different user
                mock_db_session
            )
    
    @pytest.mark.asyncio
    async def test_delete_comment_success(self, mock_db_session, sample_comment, sample_post):
        """Test successful comment deletion"""
        # Setup
        sample_post.comment_count = 1
        sample_comment.post_id = sample_post.id
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        # Mock comment query
        comment_result = MagicMock()
        comment_result.scalar_one_or_none.return_value = sample_comment
        
        # Mock post query
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = sample_post
        
        mock_db_session.execute.side_effect = [comment_result, post_result]
        
        # Test
        result = await engagement_service.delete_comment(
            str(sample_comment.id),
            sample_comment.user_id,
            mock_db_session
        )
        
        # Assertions
        assert result.success is True
        assert result.message == "Comment deleted successfully"
        assert result.comment_count == 0
        assert sample_post.comment_count == 0
        mock_db_session.delete.assert_called_once_with(sample_comment)
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_post_engagement_success(self, mock_db_session, sample_post):
        """Test getting post engagement data"""
        # Setup
        sample_post.like_count = 5
        sample_post.comment_count = 3
        
        mock_db_session.execute = AsyncMock()
        
        # Mock post query
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = sample_post
        
        # Mock user like query (user liked the post)
        like_result = MagicMock()
        like_result.scalar_one_or_none.return_value = PostLike()
        
        # Mock comments query
        comments_result = MagicMock()
        mock_comments = [
            PostComment(
                id=uuid.uuid4(),
                post_id=sample_post.id,
                user_id="user1",
                content="Comment 1",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            PostComment(
                id=uuid.uuid4(),
                post_id=sample_post.id,
                user_id="user2",
                content="Comment 2",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        comments_result.scalars.return_value.all.return_value = mock_comments
        
        mock_db_session.execute.side_effect = [post_result, like_result, comments_result]
        
        # Test
        result = await engagement_service.get_post_engagement(
            str(sample_post.id),
            "test_user_456",
            mock_db_session
        )
        
        # Assertions
        assert result is not None
        assert result.post_id == str(sample_post.id)
        assert result.like_count == 5
        assert result.comment_count == 3
        assert result.user_liked is True
        assert len(result.recent_comments) == 2
        assert result.recent_comments[0].content == "Comment 1"
    
    @pytest.mark.asyncio
    async def test_get_post_engagement_not_found(self, mock_db_session):
        """Test getting engagement for non-existent post"""
        # Setup
        mock_db_session.execute = AsyncMock()
        
        # Mock post query (no post found)
        post_result = MagicMock()
        post_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = post_result
        
        # Test
        result = await engagement_service.get_post_engagement(
            str(uuid.uuid4()),
            "test_user_456",
            mock_db_session
        )
        
        # Assertions
        assert result is None