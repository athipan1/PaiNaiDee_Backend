from datetime import datetime
from . import db


class VideoPost(db.Model):
    __tablename__ = "video_posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    caption = db.Column(db.Text)
    video_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to User
    user = db.relationship("User", backref="video_posts")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "caption": self.caption,
            "video_url": self.video_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }