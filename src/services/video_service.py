import os
from typing import Optional, List
from flask_jwt_extended import get_current_user
from src.models import db, VideoPost, User
from src.services.storage_service import StorageService


class VideoService:
    @staticmethod
    def create_video_post(user_id: int, title: str, description: str, caption: str, 
                         video_file, thumbnail_file=None) -> tuple:
        """Create a new video post with cloud storage support"""
        # Validate user exists and is admin
        user = db.session.get(User, user_id)
        if not user:
            return None, "User not found"
        
        if not user.is_admin:
            return None, "Only admin users can upload videos"

        # Save video file to storage
        video_url, video_error = StorageService.save_video_file(video_file)
        if video_error:
            return None, video_error

        # Save thumbnail file if provided
        thumbnail_url = None
        if thumbnail_file:
            thumbnail_url, thumbnail_error = StorageService.save_thumbnail_file(thumbnail_file)
            if thumbnail_error:
                # Clean up video file if thumbnail upload fails
                StorageService.delete_file(video_url)
                return None, thumbnail_error

        # Get file size
        file_size = StorageService.get_file_size(video_file)

        # Create video post record
        video_post = VideoPost(
            user_id=user_id,
            title=title,
            description=description,
            caption=caption,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            file_size=file_size
        )

        try:
            db.session.add(video_post)
            db.session.commit()
            return video_post, "Video uploaded successfully"
        except Exception as e:
            db.session.rollback()
            # Clean up uploaded files if database save fails
            StorageService.delete_file(video_url)
            if thumbnail_url:
                StorageService.delete_file(thumbnail_url)
            return None, f"Error saving video post: {str(e)}"

    @staticmethod
    def get_admin_videos(admin_id: int) -> List[VideoPost]:
        """Get all video posts for a specific admin (RLS enforcement)"""
        return (
            VideoPost.query
            .filter_by(user_id=admin_id)
            .join(User)
            .order_by(VideoPost.created_at.desc())
            .all()
        )

    @staticmethod
    def get_video_by_id(video_id: int, admin_id: int) -> Optional[VideoPost]:
        """Get a specific video by ID (RLS enforcement - admin can only see their own videos)"""
        return (
            VideoPost.query
            .filter_by(id=video_id, user_id=admin_id)
            .join(User)
            .first()
        )

    @staticmethod
    def delete_video_post(video_id: int, admin_id: int) -> tuple:
        """Delete a video post (RLS enforcement - admin can only delete their own videos)"""
        video_post = VideoService.get_video_by_id(video_id, admin_id)
        
        if not video_post:
            return False, "Video not found or you don't have permission to delete it"

        try:
            # Delete files from storage
            if video_post.video_url:
                StorageService.delete_file(video_post.video_url)
            if video_post.thumbnail_url:
                StorageService.delete_file(video_post.thumbnail_url)

            # Delete from database
            db.session.delete(video_post)
            db.session.commit()
            return True, "Video deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error deleting video: {str(e)}"

    @staticmethod
    def update_video_post(video_id: int, admin_id: int, title: str = None, 
                         description: str = None, caption: str = None) -> tuple:
        """Update a video post (RLS enforcement - admin can only update their own videos)"""
        video_post = VideoService.get_video_by_id(video_id, admin_id)
        
        if not video_post:
            return None, "Video not found or you don't have permission to update it"

        try:
            # Update fields if provided
            if title is not None:
                video_post.title = title
            if description is not None:
                video_post.description = description
            if caption is not None:
                video_post.caption = caption

            db.session.commit()
            return video_post, "Video updated successfully"
        except Exception as e:
            db.session.rollback()
            return None, f"Error updating video: {str(e)}"

    @staticmethod
    def get_all_videos() -> List[VideoPost]:
        """Get all video posts (for public feed - kept for backward compatibility)"""
        return (
            VideoPost.query
            .join(User)
            .order_by(VideoPost.created_at.desc())
            .all()
        )