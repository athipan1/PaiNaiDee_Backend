"""
Hugging Face Spaces App Entry Point
This file is required for Hugging Face Spaces deployment.
"""
import os
from flask import Flask, jsonify

def create_spaces_app():
    """Create Flask app configured for Hugging Face Spaces"""
    # Set environment variables for Spaces deployment
    os.environ['FLASK_ENV'] = 'huggingface'
    # The SECRET_KEY should be set as a secret in the Space settings
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'a-default-secret-key-for-local-dev'

    # The DATABASE_URL is expected to be set as a secret in the Space settings
    if not os.environ.get('DATABASE_URL'):
        print("WARNING: DATABASE_URL environment variable not set. Application might not connect to the database.")


    # Import and create the main app
    from src.app import create_app, db
    config_name = os.getenv('FLASK_ENV', 'huggingface')
    app = create_app(config_name)

    # Initialize the database by calling the 'init-db' command
    try:
        print("Attempting to initialize the database...")
        with app.app_context():
            app.cli.main(args=['init-db'])
        print("Database initialization command executed.")
    except Exception as e:
        print(f"An error occurred during database initialization via CLI: {e}")
        # Depending on the error, you might want to raise it to stop the app
        raise

    # Override the home route for Spaces to provide a clear entry point message
    @app.route('/')
    def spaces_home():
        return jsonify({
            "message": "🇹🇭 PaiNaiDee Backend API is running on Hugging Face Spaces!",
            "description": "The full-featured Thai Tourism API is now active.",
            "api_base": "/api",
            "github": "https://github.com/athipan1/PaiNaiDee_Backend",
            "note": "This deployment should be connected to the configured Supabase database."
        })

    # Add a health check endpoint required by the Dockerfile
    @app.route('/health')
    def health_check():
        # A simple health check. A more robust check could query the database.
        db_status = "ok"
        try:
            with app.app_context():
                db.session.execute('SELECT 1')
        except Exception as e:
            db_status = f"error: {e}"

        return jsonify({
            "status": "healthy",
            "platform": "huggingface-spaces",
            "database_connection": db_status
        })
        
    return app

# Create the app instance for Hugging Face Spaces
app = create_spaces_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # Hugging Face Spaces default port
    app.run(host="0.0.0.0", port=port, debug=False)