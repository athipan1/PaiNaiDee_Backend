import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.config import config
from src.models import db, User
from src.routes.attractions import attractions_bp
from src.routes.reviews import reviews_bp
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.search import search_bp
from src.utils.response import standardized_response
from src.errors import register_error_handlers


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if config_name == "testing":
        app.config["JWT_SECRET_KEY"] = "test-secret"
    else:
        app.config["JWT_SECRET_KEY"] = (
            "super-secret"  # Change this in your production environment!
        )

    db.init_app(app)
    CORS(
        app,
        origins=[
            "http://localhost:3000",
            "https://painaidee.com",
            "https://frontend-painaidee.web.app",
        ],
    )
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    app.register_blueprint(attractions_bp, url_prefix="/api")
    app.register_blueprint(reviews_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(booking_bp, url_prefix="/api")
    app.register_blueprint(search_bp, url_prefix="/api")

    @app.route("/")
    def home():
        return standardized_response(message="Welcome to Pai Nai Dii Backend!")

    @app.route("/health")
    def health_check():
        """Health check endpoint for frontend connectivity verification"""
        return standardized_response(
            data={
                "status": "healthy",
                "version": "1.0.0",
                "cors_enabled": True,
                "endpoints": {
                    "auth": "/api/auth/login, /api/auth/register",
                    "attractions": "/api/attractions",
                    "booking": "/api/book-room, /api/rent-car",
                    "reviews": "/api/reviews",
                    "search": "/api/search/suggestions"
                }
            },
            message="API is running and ready for frontend connections"
        )

    register_error_handlers(app)

    return app


config_name = os.getenv("FLASK_ENV", "default")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
