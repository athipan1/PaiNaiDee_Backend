from . import db
from .json_encoded_dict import JSONEncodedDict
from sqlalchemy import func


class Attraction(db.Model):
    __tablename__ = "attractions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    category = db.Column(db.String(100))
    opening_hours = db.Column(db.String(255))
    entrance_fee = db.Column(db.String(100))
    contact_phone = db.Column(db.String(100))
    website = db.Column(db.String(255))
    main_image_url = db.Column(db.String(255))
    image_urls = db.Column(JSONEncodedDict, nullable=True)

    rooms = db.relationship("Room", backref="attraction", lazy=True)
    cars = db.relationship("Car", backref="attraction", lazy=True)

    def get_review_stats(self):
        """Get average rating and total review count for this attraction."""
        from .review import Review
        result = db.session.query(
            func.avg(Review.rating).label('average_rating'),
            func.count(Review.id).label('total_reviews')
        ).filter(Review.place_id == self.id).first()
        
        avg_rating = float(result.average_rating) if result.average_rating else 0
        total_reviews = result.total_reviews or 0
        
        return {
            "average_rating": round(avg_rating, 1),
            "total_reviews": total_reviews
        }

    def to_dict(self):
        review_stats = self.get_review_stats()
        
        # Get place details if available
        place_detail = None
        if hasattr(self, 'place_details') and self.place_details:
            place_detail = self.place_details[0].to_dict() if self.place_details else None
        
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "address": self.address,
            "province": self.province,
            "district": self.district,
            "location": {"lat": self.latitude, "lng": self.longitude},
            "category": self.category,
            "opening_hours": self.opening_hours,
            "entrance_fee": self.entrance_fee,
            "contact_phone": self.contact_phone,
            "website": self.website,
            "images": self.image_urls if self.image_urls else [],
            "rooms": [room.to_dict() for room in self.rooms],
            "cars": [car.to_dict() for car in self.cars],
            "average_rating": review_stats["average_rating"],
            "total_reviews": review_stats["total_reviews"],
            "place_detail": place_detail
        }

    def to_category_dict(self):
        """Return simplified dict for category endpoint response"""
        return {
            "id": self.id,
            "name": self.name,
            "province": self.province,
            "thumbnail": self.main_image_url,
        }
