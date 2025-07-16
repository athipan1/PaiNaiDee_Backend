from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Attraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    province = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    image_urls = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Attraction {self.name}>'
