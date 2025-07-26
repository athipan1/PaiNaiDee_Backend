from . import db


class PlaceDetail(db.Model):
    __tablename__ = "place_details"

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(255))

    # Relationship to attraction
    attraction = db.relationship("Attraction", backref="place_details")

    def to_dict(self):
        return {
            "id": self.id,
            "place_id": self.place_id,
            "description": self.description,
            "link": self.link
        }