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
from src.routes.videos import videos_bp
from src.routes.dashboard import dashboard_bp
from src.routes.external_data import external_data_bp
from src.utils.response import standardized_response
from src.utils.analytics_middleware import APIAnalyticsMiddleware
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
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        headers=["Content-Type", "Authorization"],
    )
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

    # Initialize analytics middleware (disabled for testing - can be enabled with proper database setup)
    # analytics_middleware = APIAnalyticsMiddleware()
    # analytics_middleware.init_app(app)

    @app.route("/")
    def home():
        return standardized_response(message="Welcome to Pai Nai Dii Backend!")

    register_error_handlers(app)

    return app


config_name = os.getenv("FLASK_ENV", "default")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
