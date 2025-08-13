from datetime import datetime

from . import db


class DataSource(db.Model):
    __tablename__ = "data_sources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'api', 'database', 'file'
    endpoint_url = db.Column(db.String(255))
    configuration = db.Column(db.JSON)  # Store configuration as JSON
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    manual_updates = db.relationship(
        "ManualUpdate", backref="data_source", lazy=True, cascade="all, delete-orphan"
    )
    scheduled_updates = db.relationship(
        "ScheduledUpdate",
        backref="data_source",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "endpoint_url": self.endpoint_url,
            "configuration": self.configuration,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ManualUpdate(db.Model):
    __tablename__ = "manual_updates"

    id = db.Column(db.Integer, primary_key=True)
    data_source_id = db.Column(
        db.Integer, db.ForeignKey("data_sources.id"), nullable=False
    )
    status = db.Column(
        db.String(50), default="pending"
    )  # pending, running, completed, failed
    triggered_by = db.Column(db.String(100))  # user who triggered the update
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    records_processed = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "data_source_id": self.data_source_id,
            "status": self.status,
            "triggered_by": self.triggered_by,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "error_message": self.error_message,
            "records_processed": self.records_processed,
        }


class ScheduledUpdate(db.Model):
    __tablename__ = "scheduled_updates"

    id = db.Column(db.Integer, primary_key=True)
    data_source_id = db.Column(
        db.Integer, db.ForeignKey("data_sources.id"), nullable=False
    )
    frequency = db.Column(
        db.String(50), nullable=False
    )  # hourly, daily, weekly, monthly
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "data_source_id": self.data_source_id,
            "frequency": self.frequency,
            "is_active": self.is_active,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
