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
from src.routes.search import search_bp  # เพิ่มการ import blueprint สำหรับ search suggestions
from src.utils import standardized_response
from werkzeug.exceptions import HTTPException

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if config_name == 'testing':
        app.config["JWT_SECRET_KEY"] = "test-secret"
    else:
        app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in your production environment!

    db.init_app(app)
    CORS(app, origins=[
        "http://localhost:3000",
        "https://painaidee.com",
        "https://frontend-painaidee.web.app"
    ])
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    app.register_blueprint(attractions_bp, url_prefix='/api')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(booking_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')  # เพิ่มการ register blueprint สำหรับ search suggestions

    @app.route('/')
    def home():
        return standardized_response(message="Welcome to Pai Nai Dii Backend!")

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return standardized_response(message=e.description, success=False, status_code=e.code)

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        return standardized_response(message="An unexpected error occurred.", success=False, status_code=500)

    return app

config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True, port=5000)