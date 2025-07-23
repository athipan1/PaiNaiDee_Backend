import os
from src.app import create_app

if __name__ == "__main__":
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    app.run(debug=True, port=5000)
