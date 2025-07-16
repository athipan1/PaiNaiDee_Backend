import logging
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .models import db
from .routes.attractions import attractions_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)

    app.register_blueprint(attractions_bp, url_prefix='/api')

    # Basic logging
    logging.basicConfig(level=logging.INFO)

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Not Found: {error}')
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal Server Error: {error}')
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error
        app.logger.error(f"An unexpected error occurred: {e}")
        # Rollback the session in case of a database error
        db.session.rollback()
        # Return a generic 500 error response
        return jsonify({"error": "An unexpected error occurred"}), 500

    @app.route('/')
    def home():
        return "Welcome to Pai Nai Dee Backend!"

    return app
