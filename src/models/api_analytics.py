from datetime import datetime
from src.models import db


class APIAnalytics(db.Model):
    """Model to track API request analytics for dashboard monitoring"""

    __tablename__ = 'api_analytics'

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(255), nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False, index=True)
    response_time = db.Column(db.Float, nullable=False)  # in milliseconds
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    source_ip = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.Text, nullable=True)
    request_size = db.Column(db.Integer, nullable=True)  # in bytes
    response_size = db.Column(db.Integer, nullable=True)  # in bytes
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    user = db.relationship('User', backref='api_requests', lazy=True)

    def __repr__(self):
        return f'<APIAnalytics {self.method} {self.endpoint} - {self.status_code}>'

    def to_dict(self):
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source_ip': self.source_ip,
            'user_agent': self.user_agent,
            'request_size': self.request_size,
            'response_size': self.response_size,
            'user_id': self.user_id
        }
