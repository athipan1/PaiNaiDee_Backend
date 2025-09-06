from datetime import datetime
from . import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="posts")
    comments = db.relationship("Comment", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")
    likes = db.relationship("Like", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "likes_count": self.likes.count(),
            "comments_count": self.comments.count()
        }

class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=True)
    video_post_id = db.Column(db.Integer, db.ForeignKey("video_posts.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="likes")
    post = db.relationship("Post", back_populates="likes")
    video_post = db.relationship("VideoPost", back_populates="likes")

    __table_args__ = (
        db.CheckConstraint('(post_id IS NOT NULL AND video_post_id IS NULL) OR (post_id IS NULL AND video_post_id IS NOT NULL)', name='like_target_check'),
    )

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=True)
    video_post_id = db.Column(db.Integer, db.ForeignKey("video_posts.id"), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="comments")
    post = db.relationship("Post", back_populates="comments")
    video_post = db.relationship("VideoPost", back_populates="comments")

    __table_args__ = (
        db.CheckConstraint('(post_id IS NOT NULL AND video_post_id IS NULL) OR (post_id IS NULL AND video_post_id IS NOT NULL)', name='comment_target_check'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "post_id": self.post_id,
            "video_post_id": self.video_post_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
