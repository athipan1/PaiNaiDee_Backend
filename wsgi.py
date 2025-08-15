import os
from src.app import create_app

# Create the Flask app for WSGI servers (gunicorn)
app = create_app(os.environ.get("FLASK_ENV", "production"))

if __name__ == '__main__':
    # For local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)