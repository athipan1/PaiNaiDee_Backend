from datetime import datetime
from . import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False) # e.g., pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    # Relationship to Project
    project = db.relationship('Project', back_populates='tasks')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
