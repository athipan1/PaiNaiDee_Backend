from datetime import datetime
from . import db


# Association table for the follower relationship
user_follows = db.Table('user_follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Project
    projects = db.relationship('Project', back_populates='user', lazy='dynamic')

    # Self-referential many-to-many relationship for followers
    followed = db.relationship(
        'User', secondary=user_follows,
        primaryjoin=(id == user_follows.c.follower_id),
        secondaryjoin=(id == user_follows.c.followed_id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "following_count": self.followed.count(),
            "followers_count": self.followers.count()
        }
