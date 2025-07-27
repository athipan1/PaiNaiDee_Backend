from . import db
from datetime import datetime, timezone


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    attraction_id = db.Column(
        db.Integer, db.ForeignKey("attractions.id"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=1)
    amenities = db.Column(db.JSON)  # Store amenities as JSON array
    image_urls = db.Column(db.JSON)  # Store image URLs as JSON array
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "attraction_id": self.attraction_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "capacity": self.capacity,
            "amenities": self.amenities or [],
            "image_urls": self.image_urls or [],
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def to_summary_dict(self):
        """Return a summary version for listing endpoints"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "capacity": self.capacity,
            "is_available": self.is_available
        }
