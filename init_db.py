import os
from src.app import create_app
from src.models import db

def init_database():
    config_name = os.getenv('FLASK_ENV', 'default')
    app = create_app(config_name)
    with app.app_context():
        db.create_all()
    print("Database initialized.")

if __name__ == "__main__":
    init_database()
