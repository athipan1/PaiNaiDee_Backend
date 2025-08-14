import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, ARRAY, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from app.db.session import Base


class Location(Base):
    """Location model for Phase 1"""
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    province = Column(Text, nullable=True)
    aliases = Column(ARRAY(Text), default=[])
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    popularity_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    posts = relationship("Post", back_populates="location")

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', province='{self.province}')>"


class Post(Base):
    """Post model for Phase 1 (augmented from existing attractions)"""
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Text, nullable=False)  # TODO: Link to user system
    caption = Column(Text, nullable=True)
    tags = Column(ARRAY(Text), default=[])
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    lat = Column(Float, nullable=True)  # Fallback if PostGIS not available
    lng = Column(Float, nullable=True)  # Fallback if PostGIS not available
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    location = relationship("Location", back_populates="posts")
    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, user_id='{self.user_id}', location_id={self.location_id})>"


class PostMedia(Base):
    """Post media model for Phase 1"""
    __tablename__ = "post_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String(20), nullable=False)  # 'image' or 'video'
    url = Column(Text, nullable=False)
    thumb_url = Column(Text, nullable=True)
    ordering = Column(Integer, default=0)

    # Relationships
    post = relationship("Post", back_populates="media")

    def __repr__(self):
        return f"<PostMedia(id={self.id}, post_id={self.post_id}, type='{self.media_type}')>"


class PostLike(Base):
    """Post like model for community engagement"""
    __tablename__ = "post_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Text, nullable=False)  # TODO: Link to user system
    created_at = Column(DateTime, default=func.now())

    # Relationships
    post = relationship("Post", backref="likes")

    def __repr__(self):
        return f"<PostLike(id={self.id}, post_id={self.post_id}, user_id='{self.user_id}')>"


class PostComment(Base):
    """Post comment model for community engagement"""
    __tablename__ = "post_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Text, nullable=False)  # TODO: Link to user system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    post = relationship("Post", backref="comments")

    def __repr__(self):
        return f"<PostComment(id={self.id}, post_id={self.post_id}, user_id='{self.user_id}')>"


# Indexes for performance
Index('idx_locations_name_trgm', Location.name, postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
Index('idx_locations_aliases', Location.aliases, postgresql_using='gin')
Index('idx_posts_tags', Post.tags, postgresql_using='gin')
Index('idx_posts_location_id', Post.location_id)
Index('idx_posts_created_at', Post.created_at)
Index('idx_posts_like_count', Post.like_count)
Index('idx_post_media_post_id', PostMedia.post_id)
Index('idx_post_likes_post_id', PostLike.post_id)
Index('idx_post_likes_user_id', PostLike.user_id)
Index('idx_post_comments_post_id', PostComment.post_id)
Index('idx_post_comments_user_id', PostComment.user_id)
Index('idx_post_comments_created_at', PostComment.created_at)