import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from src.config import config
from src.models import db, User
from src.routes.attractions import attractions_bp
from src.routes.reviews import reviews_bp
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.search import search_bp
from src.routes.videos import videos_bp
from src.routes.rooms import rooms_bp
from src.utils.response import standardized_response
from src.errors import register_error_handlers


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # JWT Configuration
    if config_name == "testing":
        app.config["JWT_SECRET_KEY"] = "test-secret"
    else:
        app.config["JWT_SECRET_KEY"] = app.config.get("JWT_SECRET_KEY", "super-secret")

    # Database initialization
    db.init_app(app)
    
    # CORS Configuration with environment variables
    CORS(
        app,
        origins=app.config.get("CORS_ORIGINS", [
            "http://localhost:3000",
            "https://painaidee.com",
            "https://frontend-painaidee.web.app",
        ]),
        allow_headers=["Content-Type", "Authorization"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    # JWT Manager
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    # Swagger Configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "PaiNaiDee Backend API",
            "description": "API for managing rooms, attractions, and bookings for the PaiNaiDee platform",
            "version": app.config.get("API_VERSION", "v1"),
            "contact": {
                "name": "PaiNaiDee Team",
                "url": app.config.get("BASE_URL", "http://localhost:5000"),
            }
        },
        "host": app.config.get("BASE_URL", "localhost:5000").replace("http://", "").replace("https://", ""),
        "basePath": f"/api/{app.config.get('API_VERSION', 'v1')}",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "JWT": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT token. Format: Bearer <token>"
            }
        }
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)

    # API Version prefix
    api_version = app.config.get("API_VERSION", "v1")
    api_prefix = f"/api/{api_version}"

    # Blueprint registration with versioning
    app.register_blueprint(attractions_bp, url_prefix=api_prefix)
    app.register_blueprint(reviews_bp, url_prefix=api_prefix)
    app.register_blueprint(auth_bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(booking_bp, url_prefix=api_prefix)
    app.register_blueprint(search_bp, url_prefix=api_prefix)
    app.register_blueprint(videos_bp, url_prefix=api_prefix)
    app.register_blueprint(rooms_bp, url_prefix=api_prefix)

    @app.route("/")
    def home():
        """
        Welcome endpoint
        ---
        responses:
          200:
            description: Welcome message
            schema:
              type: object
              properties:
                success:
                  type: boolean
                message:
                  type: string
                data:
                  type: object
        """
        return standardized_response(
            message="Welcome to PaiNaiDee Backend API!",
            data={
                "version": api_version,
                "documentation": f"{app.config.get('BASE_URL', 'http://localhost:5000')}/api/docs/",
                "environment": app.config.get("ENVIRONMENT", "development")
            }
        )

    @app.route("/health")
    def health_check():
        """
        Health check endpoint
        ---
        responses:
          200:
            description: Service health status
            schema:
              type: object
              properties:
                success:
                  type: boolean
                message:
                  type: string
                data:
                  type: object
                  properties:
                    status:
                      type: string
                    version:
                      type: string
                    environment:
                      type: string
        """
        return standardized_response(
            message="Service is healthy",
            data={
                "status": "healthy",
                "version": api_version,
                "environment": app.config.get("ENVIRONMENT", "development")
            }
        )

    register_error_handlers(app)

    return app


config_name = os.getenv("FLASK_ENV", "default")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
