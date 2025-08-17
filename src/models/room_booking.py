from . import db
from datetime import datetime, timezone


class RoomBooking(db.Model):
    __tablename__ = "room_bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default="active", nullable=False)  # active, cancelled

    # Relationships
    user = db.relationship("User", backref="room_bookings")
    room = db.relationship("Room", backref="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "room_id": self.room_id,
            "date_start": self.date_start.isoformat(),
            "date_end": self.date_end.isoformat(),
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }
