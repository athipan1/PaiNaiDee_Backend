import os
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from src.config import config
from src.models import db
from src.routes.attractions import attractions_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    CORS(app)

    app.register_blueprint(attractions_bp, url_prefix='/api')

    @app.route('/')
    def home():
        response = make_response(jsonify(message="Welcome to Pai Nai Dii Backend!"))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    return app

config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
