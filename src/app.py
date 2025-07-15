from flask import Flask
from flask_cors import CORS
from .config import Config
from .models import db
from .routes.attractions import attractions_bp

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .models import db
from .routes.attractions import attractions_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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
        return jsonify({'error': 'Internal Server Error'}), 500

    @app.route('/')
    def home():
        return "Welcome to Pai Nai Dee Backend!"

    return app
