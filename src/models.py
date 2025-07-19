import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import TypeDecorator, TEXT

db = SQLAlchemy()

class JSONEncodedDict(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

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
    image_urls = db.Column(JSONEncodedDict, nullable=True)

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

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'place_id': self.place_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
        }
