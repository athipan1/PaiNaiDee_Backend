import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.config import config
from src.models import db, User
from src.routes.attractions import attractions_bp
from src.routes.reviews import reviews_bp
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.search import search_bp
from src.routes.videos import videos_bp
from src.routes.dashboard import dashboard_bp
from src.routes.external_data import external_data_bp
from src.routes.talk import talk_bp
from src.utils.response import standardized_response
from src.utils.analytics_middleware import APIAnalyticsMiddleware
from src.errors import register_error_handlers


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if config_name == "testing":
        app.config["JWT_SECRET_KEY"] = "test-secret"
    else:
        # For production, JWT_SECRET_KEY must be set as an environment variable.
        app.config["JWT_SECRET_KEY"] = os.environ.get(
            "JWT_SECRET_KEY", "a-secure-default-secret-for-development"
        )

    db.init_app(app)

    # ✅ Allow production + development domains
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://pai-naidee-ui-spark.vercel.app",  # production frontend
                "http://localhost:3000",                   # React dev
                "http://127.0.0.1:3000",                   # React dev alternative
                "http://127.0.0.1:5500",                   # static HTML dev
            ]
        }
    })
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    app.register_blueprint(attractions_bp, url_prefix="/api")
    app.register_blueprint(reviews_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(booking_bp, url_prefix="/api")
    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(videos_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(external_data_bp, url_prefix="/api")
    app.register_blueprint(talk_bp, url_prefix="/api")

    # Initialize analytics middleware (disabled for testing - can be enabled with proper database setup)
    # analytics_middleware = APIAnalyticsMiddleware()
    # analytics_middleware.init_app(app)

    @app.route("/")
    def home():
        return standardized_response(message="Welcome to Pai Nai Dii Backend!")

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"})

    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db_command():
        """Creates the database tables."""
        # Import all models here to ensure they are registered with SQLAlchemy
        from src import models
        db.create_all()
        print("Initialized the database.")

    return app


if __name__ == "__main__":
    # This block is for local development only.
    # In production, the app is created and run by a WSGI server like Gunicorn via wsgi.py.
    config_name = os.getenv("FLASK_ENV", "development")
    app = create_app(config_name)
    port = int(os.environ.get("PORT", 5000))
    # Debug mode should only be enabled in development
    is_debug = config_name == "development"
    app.run(host="0.0.0.0", port=port, debug=is_debug)
