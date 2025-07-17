from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

db = SQLAlchemy()

class Attraction(db.Model):
    __tablename__ = 'attractions'

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
    image_urls = db.Column(ARRAY(db.String))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'province': self.province,
            'district': self.district,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'category': self.category,
            'opening_hours': self.opening_hours,
            'entrance_fee': self.entrance_fee,
            'contact_phone': self.contact_phone,
            'website': self.website,
            'main_image_url': self.main_image_url,
            'image_urls': self.image_urls,
        }
