from . import db
from sqlalchemy import func


class Attraction(db.Model):
    __tablename__ = "attractions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.Text)
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    address = db.Column(db.Text)

    def to_dict(self, average_rating=None, total_reviews=None):
        # The method now accepts review statistics as parameters, avoiding a database call.
        # Default values are provided to handle cases where an attraction has no reviews.
        try:
            avg_rating_val = round(float(average_rating), 1) if average_rating is not None else 0.0
        except (ValueError, TypeError):
            avg_rating_val = 0.0

        total_reviews_val = total_reviews or 0

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "province": self.province,
            "district": self.district,
            "address": self.address,
            "average_rating": avg_rating_val,
            "total_reviews": total_reviews_val,
        }
