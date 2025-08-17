from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, and_, desc
import uuid
from datetime import datetime, timezone

from app.db.models import Post, PostLike, PostComment
from app.schemas.engagement import (
    PostLikeCreate, PostLikeResponse,
    PostCommentCreate, PostCommentUpdate, PostCommentResponse,
    PostEngagementResponse, EngagementActionResponse
)
from app.core.logging import logger


class EngagementService:
    """Service for post engagement operations (likes and comments)"""

    async def like_post(
        self,
        post_id: str,
        user_id: str,
        db: AsyncSession
    ) -> EngagementActionResponse:
        """
        Like a post. If already liked, this will unlike the post.

        Args:
            post_id: Post UUID to like
            user_id: User ID (from auth)
            db: Database session

        Returns:
            EngagementActionResponse
        """
        try:
            post_uuid = uuid.UUID(post_id)
        except ValueError:
            return EngagementActionResponse(
                success=False,
                message="Invalid post ID format"
            )

        # Check if post exists
        post_query = select(Post).where(Post.id == post_uuid)
        post_result = await db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            return EngagementActionResponse(
                success=False,
                message="Post not found"
            )

        # Check if user already liked this post
        like_query = select(PostLike).where(
            and_(PostLike.post_id == post_uuid, PostLike.user_id == user_id)
        )
        like_result = await db.execute(like_query)
        existing_like = like_result.scalar_one_or_none()

        if existing_like:
            # Unlike the post
            await db.delete(existing_like)
            post.like_count = max(0, post.like_count - 1)
            await db.commit()

            logger.post_unliked(post_id=post_id, user_id=user_id)

            return EngagementActionResponse(
                success=True,
                message="Post unliked successfully",
                like_count=post.like_count
            )
        else:
            # Like the post
            new_like = PostLike(
                post_id=post_uuid,
                user_id=user_id
            )
            db.add(new_like)
            post.like_count += 1
            await db.commit()

            logger.post_liked(post_id=post_id, user_id=user_id)

            return EngagementActionResponse(
                success=True,
                message="Post liked successfully",
                like_count=post.like_count
            )

    async def comment_on_post(
        self,
        comment_data: PostCommentCreate,
        user_id: str,
        db: AsyncSession
    ) -> PostCommentResponse:
        """
        Add a comment to a post

        Args:
            comment_data: Comment creation data
            user_id: User ID (from auth)
            db: Database session

        Returns:
            PostCommentResponse
        """
        try:
            post_uuid = uuid.UUID(comment_data.post_id)
        except ValueError:
            raise ValueError("Invalid post ID format")

        # Check if post exists
        post_query = select(Post).where(Post.id == post_uuid)
        post_result = await db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            raise ValueError("Post not found")

        # Create comment
        new_comment = PostComment(
            post_id=post_uuid,
            user_id=user_id,
            content=comment_data.content
        )

        db.add(new_comment)
        post.comment_count += 1
        await db.flush()
        await db.commit()
        await db.refresh(new_comment)

        logger.post_commented(
            post_id=comment_data.post_id,
            user_id=user_id,
            comment_id=str(new_comment.id)
        )

        # Application-level fallback for timestamps if database defaults fail
        current_time = datetime.now(timezone.utc)
        created_at = new_comment.created_at or current_time
        updated_at = new_comment.updated_at or current_time

        return PostCommentResponse(
            id=str(new_comment.id),
            post_id=str(new_comment.post_id),
            user_id=new_comment.user_id,
            content=new_comment.content,
            created_at=created_at,
            updated_at=updated_at
        )

    async def update_comment(
        self,
        comment_id: str,
        comment_data: PostCommentUpdate,
        user_id: str,
        db: AsyncSession
    ) -> PostCommentResponse:
        """
        Update a comment (only by the comment author)

        Args:
            comment_id: Comment UUID to update
            comment_data: Comment update data
            user_id: User ID (from auth)
            db: Database session

        Returns:
            PostCommentResponse
        """
        try:
            comment_uuid = uuid.UUID(comment_id)
        except ValueError:
            raise ValueError("Invalid comment ID format")

        # Get comment and verify ownership
        comment_query = select(PostComment).where(PostComment.id == comment_uuid)
        comment_result = await db.execute(comment_query)
        comment = comment_result.scalar_one_or_none()

        if not comment:
            raise ValueError("Comment not found")

        if comment.user_id != user_id:
            raise PermissionError("You can only edit your own comments")

        # Update comment
        comment.content = comment_data.content
        await db.commit()
        await db.refresh(comment)

        logger.comment_updated(
            comment_id=comment_id,
            user_id=user_id
        )

        # Application-level fallback for timestamps if database defaults fail
        current_time = datetime.now(timezone.utc)
        created_at = comment.created_at or current_time
        updated_at = comment.updated_at or current_time

        return PostCommentResponse(
            id=str(comment.id),
            post_id=str(comment.post_id),
            user_id=comment.user_id,
            content=comment.content,
            created_at=created_at,
            updated_at=updated_at
        )

    async def delete_comment(
        self,
        comment_id: str,
        user_id: str,
        db: AsyncSession
    ) -> EngagementActionResponse:
        """
        Delete a comment (only by the comment author)

        Args:
            comment_id: Comment UUID to delete
            user_id: User ID (from auth)
            db: Database session

        Returns:
            EngagementActionResponse
        """
        try:
            comment_uuid = uuid.UUID(comment_id)
        except ValueError:
            return EngagementActionResponse(
                success=False,
                message="Invalid comment ID format"
            )

        # Get comment and verify ownership
        comment_query = select(PostComment).where(PostComment.id == comment_uuid)
        comment_result = await db.execute(comment_query)
        comment = comment_result.scalar_one_or_none()

        if not comment:
            return EngagementActionResponse(
                success=False,
                message="Comment not found"
            )

        if comment.user_id != user_id:
            return EngagementActionResponse(
                success=False,
                message="You can only delete your own comments"
            )

        # Update post comment count
        post_query = select(Post).where(Post.id == comment.post_id)
        post_result = await db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if post:
            post.comment_count = max(0, post.comment_count - 1)

        # Delete comment
        await db.delete(comment)
        await db.commit()

        logger.comment_deleted(
            comment_id=comment_id,
            user_id=user_id
        )

        return EngagementActionResponse(
            success=True,
            message="Comment deleted successfully",
            comment_count=post.comment_count if post else None
        )

    async def get_post_engagement(
        self,
        post_id: str,
        user_id: str,
        db: AsyncSession,
        limit_comments: int = 5
    ) -> Optional[PostEngagementResponse]:
        """
        Get engagement data for a post (likes, comments, user's like status)

        Args:
            post_id: Post UUID
            user_id: Current user ID
            db: Database session
            limit_comments: Number of recent comments to include

        Returns:
            PostEngagementResponse or None
        """
        try:
            post_uuid = uuid.UUID(post_id)
        except ValueError:
            return None

        # Get post
        post_query = select(Post).where(Post.id == post_uuid)
        post_result = await db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            return None

        # Check if user liked this post
        user_like_query = select(PostLike).where(
            and_(PostLike.post_id == post_uuid, PostLike.user_id == user_id)
        )
        user_like_result = await db.execute(user_like_query)
        user_liked = user_like_result.scalar_one_or_none() is not None

        # Get recent comments
        comments_query = (
            select(PostComment)
            .where(PostComment.post_id == post_uuid)
            .order_by(desc(PostComment.created_at))
            .limit(limit_comments)
        )
        comments_result = await db.execute(comments_query)
        comments = comments_result.scalars().all()

        # Application-level fallback for timestamps if database defaults fail
        current_time = datetime.now(timezone.utc)
        recent_comments = [
            PostCommentResponse(
                id=str(comment.id),
                post_id=str(comment.post_id),
                user_id=comment.user_id,
                content=comment.content,
                created_at=comment.created_at or current_time,
                updated_at=comment.updated_at or current_time
            )
            for comment in comments
        ]

        return PostEngagementResponse(
            post_id=post_id,
            like_count=post.like_count,
            comment_count=post.comment_count,
            user_liked=user_liked,
            recent_comments=recent_comments
        )


# Global service instance
engagement_service = EngagementService()
