"""
Storage service for handling media uploads to cloud storage.
Supports both Supabase and Firebase storage backends.
"""

import os
import uuid
from typing import Optional, Tuple, BinaryIO
from abc import ABC, abstractmethod
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def upload_file(
        self, 
        file: UploadFile, 
        bucket: str, 
        file_path: str
    ) -> Tuple[str, Optional[str]]:
        """
        Upload file to storage backend
        
        Returns:
            Tuple of (file_url, thumbnail_url)
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """Delete file from storage backend"""
        pass


class DemoStorageBackend(StorageBackend):
    """Demo storage backend that creates mock URLs for development"""
    
    def __init__(self, base_url: str = "https://storage.example.com"):
        self.base_url = base_url
    
    async def upload_file(
        self, 
        file: UploadFile, 
        bucket: str, 
        file_path: str
    ) -> Tuple[str, Optional[str]]:
        """Create demo URLs for uploaded files"""
        # Generate unique filename
        file_extension = os.path.splitext(file.filename or "file")[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create demo URLs
        file_url = f"{self.base_url}/{bucket}/{file_path}/{unique_filename}"
        
        # Create thumbnail URL for videos
        thumbnail_url = None
        if file.content_type and file.content_type.startswith('video/'):
            thumbnail_url = f"{self.base_url}/{bucket}/{file_path}/thumb_{unique_filename}.jpg"
        
        logger.info(f"Demo upload: {file.filename} -> {file_url}")
        
        return file_url, thumbnail_url
    
    async def delete_file(self, file_url: str) -> bool:
        """Mock file deletion"""
        logger.info(f"Demo delete: {file_url}")
        return True


class SupabaseStorageBackend(StorageBackend):
    """Supabase storage backend"""
    
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        # TODO: Initialize Supabase client
        logger.warning("Supabase storage not fully implemented - using demo mode")
    
    async def upload_file(
        self, 
        file: UploadFile, 
        bucket: str, 
        file_path: str
    ) -> Tuple[str, Optional[str]]:
        """Upload file to Supabase storage"""
        # TODO: Implement actual Supabase upload
        # For now, fallback to demo mode
        demo_backend = DemoStorageBackend("https://supabase-demo.example.com")
        return await demo_backend.upload_file(file, bucket, file_path)
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete file from Supabase storage"""
        # TODO: Implement actual Supabase deletion
        logger.info(f"Supabase delete (demo): {file_url}")
        return True


class FirebaseStorageBackend(StorageBackend):
    """Firebase storage backend"""
    
    def __init__(self, credentials_path: str, bucket_name: str):
        self.credentials_path = credentials_path
        self.bucket_name = bucket_name
        # TODO: Initialize Firebase client
        logger.warning("Firebase storage not fully implemented - using demo mode")
    
    async def upload_file(
        self, 
        file: UploadFile, 
        bucket: str, 
        file_path: str
    ) -> Tuple[str, Optional[str]]:
        """Upload file to Firebase storage"""
        # TODO: Implement actual Firebase upload
        # For now, fallback to demo mode
        demo_backend = DemoStorageBackend("https://firebase-demo.example.com")
        return await demo_backend.upload_file(file, bucket, file_path)
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete file from Firebase storage"""
        # TODO: Implement actual Firebase deletion
        logger.info(f"Firebase delete (demo): {file_url}")
        return True


class StorageService:
    """Main storage service that delegates to configured backend"""
    
    def __init__(self):
        self.backend = self._get_storage_backend()
    
    def _get_storage_backend(self) -> StorageBackend:
        """Get storage backend based on configuration"""
        storage_type = os.getenv("STORAGE_TYPE", "demo").lower()
        
        if storage_type == "supabase":
            url = os.getenv("SUPABASE_URL")
            api_key = os.getenv("SUPABASE_API_KEY")
            if url and api_key:
                return SupabaseStorageBackend(url, api_key)
            else:
                logger.warning("Supabase credentials not found, using demo storage")
                return DemoStorageBackend()
        
        elif storage_type == "firebase":
            credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            bucket_name = os.getenv("FIREBASE_BUCKET_NAME")
            if credentials_path and bucket_name:
                return FirebaseStorageBackend(credentials_path, bucket_name)
            else:
                logger.warning("Firebase credentials not found, using demo storage")
                return DemoStorageBackend()
        
        else:
            # Default to demo storage for development
            return DemoStorageBackend()
    
    async def upload_media(
        self, 
        file: UploadFile, 
        user_id: str, 
        post_id: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Upload media file for a post
        
        Args:
            file: Uploaded file
            user_id: User ID
            post_id: Optional post ID for organizing files
            
        Returns:
            Tuple of (file_url, thumbnail_url)
        """
        # Validate file type
        if not file.content_type or not (
            file.content_type.startswith('image/') or 
            file.content_type.startswith('video/')
        ):
            raise ValueError(f"Unsupported file type: {file.content_type}")
        
        # Validate file size (10MB limit for demo)
        max_size = 10 * 1024 * 1024  # 10MB
        if hasattr(file, 'size') and file.size and file.size > max_size:
            raise ValueError(f"File too large. Maximum size is {max_size // (1024*1024)}MB")
        
        # Organize files by user and date
        bucket = "community-posts"
        file_path = f"users/{user_id}"
        if post_id:
            file_path += f"/posts/{post_id}"
        
        # Upload to storage backend
        file_url, thumbnail_url = await self.backend.upload_file(file, bucket, file_path)
        
        logger.info(f"Media uploaded: {file.filename} -> {file_url}")
        
        return file_url, thumbnail_url
    
    async def delete_media(self, file_url: str) -> bool:
        """Delete media file"""
        return await self.backend.delete_file(file_url)
    
    def is_image(self, content_type: str) -> bool:
        """Check if content type is an image"""
        return content_type.startswith('image/')
    
    def is_video(self, content_type: str) -> bool:
        """Check if content type is a video"""
        return content_type.startswith('video/')


# Global storage service instance
storage_service = StorageService()