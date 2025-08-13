"""
Flask application factory and main app package.

This module contains the create_app function which sets up the Flask application
with all necessary extensions, blueprints, and configuration.
"""

import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import config
from .errors import register_error_handlers
from .extensions import db, migrate
from .models import User
from .utils.response import standardized_response


def create_app(config_name=None):
    """
    Application factory function to create and configure Flask app.

    Args:
        config_name (str): Configuration name (development, production, testing, etc.)

    Returns:
        Flask: Configured Flask application instance
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Validate configuration
    config[config_name].validate_required_config()

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup CORS
    CORS(
        app,
        origins=app.config.get("CORS_ORIGINS", ["http://localhost:3000"]),
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # Setup JWT
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route("/")
    def home():
        return standardized_response(
            message="Welcome to PaiNaiDee Backend!",
            data={
                "version": "2.0",
                "environment": app.config.get("APP_ENV", "unknown"),
                "features": {
                    "search": True,
                    "autocomplete": app.config.get("FEATURE_AUTOCOMPLETE", False),
                    "nearby_locations": app.config.get("FEATURE_NEARBY", False),
                    "analytics": app.config.get("ENABLE_ANALYTICS", False),
                },
            },
        )

    @app.route("/health")
    def health_check():
        return standardized_response(
            message="API is healthy",
            data={
                "status": "healthy",
                "database": "connected" if db.engine else "disconnected",
            },
        )

    return app


def register_blueprints(app):
    """Register all application blueprints."""
    # Import blueprints here to avoid circular imports
    from .blueprints.api.attractions import attractions_bp
    from .blueprints.api.auth import auth_bp
    from .blueprints.api.booking import booking_bp
    from .blueprints.api.dashboard import dashboard_bp
    from .blueprints.api.external_data import external_data_bp
    from .blueprints.api.reviews import reviews_bp
    from .blueprints.api.search import search_bp
    from .blueprints.api.talk import talk_bp
    from .blueprints.api.videos import videos_bp

    # Register existing blueprints with API prefix
    app.register_blueprint(attractions_bp, url_prefix="/api")
    app.register_blueprint(reviews_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(booking_bp, url_prefix="/api")
    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(videos_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(external_data_bp, url_prefix="/api")
    app.register_blueprint(talk_bp, url_prefix="/api")
