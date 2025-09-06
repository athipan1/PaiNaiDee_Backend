import os
from src.app import create_app
from src.models import db

# Use the 'development' configuration, which should be sufficient for DB operations.
# The config might point to a local SQLite DB file, which is fine for this task.
config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name)

# The db.create_all() call needs to be within an application context.
with app.app_context():
    print("Creating all database tables...")
    # This imports all models and creates the tables.
    from src import models
    db.create_all()
    print("Database tables created successfully.")
