from . import db
from .json_encoded_dict import JSONEncodedDict


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

    def to_dict(self):
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
        }

    def to_category_dict(self):
        """Return simplified dict for category endpoint response"""
        return {
            "id": self.id,
            "name": self.name,
            "province": self.province,
            "thumbnail": self.main_image_url,
        }
