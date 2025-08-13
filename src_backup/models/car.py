from . import db


class Car(db.Model):
    __tablename__ = "cars"

    id = db.Column(db.Integer, primary_key=True)
    attraction_id = db.Column(
        db.Integer, db.ForeignKey("attractions.id"), nullable=False
    )
    brand = db.Column(db.String(100), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "price_per_day": self.price_per_day,
        }
