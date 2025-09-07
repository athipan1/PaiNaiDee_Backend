# Import the new Base from the 'app' directory structure
from app.db.session import Base
# Import SQLAlchemy components directly
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, func, UniqueConstraint
# Import the custom type
from src.models.json_encoded_dict import JSONEncodedDict


class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    province = Column(String(100))
    district = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    category = Column(String(100))
    opening_hours = Column(String(255))
    entrance_fee = Column(String(100))
    contact_phone = Column(String(100))
    website = Column(String(255))
    main_image_url = Column(String(255))
    image_urls = Column(JSONEncodedDict, nullable=True)

    # New fields for data pipeline
    source = Column(String(100), nullable=True)
    source_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # __table_args__ needs to be inside the class body
    __table_args__ = (
        UniqueConstraint('source', 'source_id', name='uq_attraction_source_source_id'),
    )

    # NOTE: Relationships to 'Room' and 'Car' are commented out because those models
    # are part of the legacy 'src' structure and would cause import errors.
    # This refactoring focuses on making the 'Attraction' model compatible with Alembic.
    # rooms = relationship("Room", backref="attraction", lazy=True)
    # cars = relationship("Car", backref="attraction", lazy=True)

    def to_dict(self, average_rating=None, total_reviews=None):
        try:
            avg_rating_val = round(float(average_rating), 1) if average_rating is not None else 0.0
        except (ValueError, TypeError):
            avg_rating_val = 0.0

        total_reviews_val = total_reviews or 0

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "province": self.province,
            "district": self.district,
            "location": {"lat": self.latitude, "lng": self.longitude},
            "category": self.category,
            "opening_hours": self.opening_hours,
            "entrance_fee": self.entrance_fee,
            "contact_phone": self.contact_phone,
            "website": self.website,
            "image_url": self.main_image_url,
            "images": self.image_urls if self.image_urls else [],
            # "rooms": [room.to_dict() for room in self.rooms], # Commented out due to relationship removal
            # "cars": [car.to_dict() for car in self.cars], # Commented out due to relationship removal
            "average_rating": avg_rating_val,
            "total_reviews": total_reviews_val,
        }

    def to_category_dict(self):
        """Return simplified dict for category endpoint response"""
        return {
            "id": self.id,
            "name": self.name,
            "province": self.province,
            "thumbnail": self.main_image_url,
        }
