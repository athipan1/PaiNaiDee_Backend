from datetime import datetime
from . import db


class VideoPost(db.Model):
    __tablename__ = "video_posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    caption = db.Column(db.Text)
    video_url = db.Column(db.String(255), nullable=False)
    thumbnail_url = db.Column(db.String(255))
    duration = db.Column(db.Integer)  # in seconds
    file_size = db.Column(db.Integer)  # in bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = db.relationship("User", backref="video_posts")
    likes = db.relationship("VideoLike", backref="video_post", lazy="dynamic", cascade="all, delete-orphan")
    comments = db.relationship("VideoComment", backref="video_post", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "title": self.title,
            "description": self.description,
            "caption": self.caption,
            "video_url": self.video_url,
            "thumbnail_url": self.thumbnail_url,
            "duration": self.duration,
            "file_size": self.file_size,
            "likes_count": self.likes.count(),
            "comments_count": self.comments.count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VideoLike(db.Model):
    __tablename__ = "video_likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    video_post_id = db.Column(db.Integer, db.ForeignKey("video_posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="video_likes")

    __table_args__ = (db.UniqueConstraint('user_id', 'video_post_id', name='_user_video_uc'),)


class VideoComment(db.Model):
    __tablename__ = "video_comments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    video_post_id = db.Column(db.Integer, db.ForeignKey("video_posts.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="video_comments")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "video_post_id": self.video_post_id,
            "text": self.text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }