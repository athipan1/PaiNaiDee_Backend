"""
Application entry point.

This module creates and runs the Flask application using the app factory pattern.
"""

import os
from app import create_app

# Create the app instance
config_name = os.getenv("FLASK_ENV", "default")
app = create_app(config_name)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = config_name == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)