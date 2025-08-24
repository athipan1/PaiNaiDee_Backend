"""
Hugging Face Spaces App Entry Point
This file is required for Hugging Face Spaces deployment.
"""
import os
import tempfile
import sqlite3
from flask import Flask, jsonify

def setup_sqlite_database():
    """Setup SQLite database for Hugging Face Spaces deployment"""
    # Create a temporary database file
    db_path = os.path.join(tempfile.gettempdir(), 'painaidee.db')
    
    # Create basic tables for demo purposes
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a simple attractions table for demo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            province TEXT,
            category TEXT,
            rating REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert some sample data
    sample_attractions = [
        ('วัดพระแก้ว', 'วัดพระแก้วมรกต วัดสำคัญในกรุงเทพฯ', 'กรุงเทพมหานคร', 'วัด', 4.8),
        ('เขาใหญ่', 'อุทยานแห่งชาติเขาใหญ่', 'นครราชสีมา', 'ธรรมชาติ', 4.5),
        ('เกาะสมุย', 'เกาะสวยในอ่าวไทย', 'สุราษฎร์ธานี', 'ชายหาด', 4.6),
        ('พระราชวังเก่า', 'พระราชวังเก่าในกรุงเทพฯ', 'กรุงเทพมหานคร', 'ประวัติศาสตร์', 4.7),
        ('ดอยสุเทพ', 'วัดพระธาตุดอยสุเทพ', 'เชียงใหม่', 'วัด', 4.9)
    ]
    
    cursor.executemany(
        'INSERT INTO attractions (name, description, province, category, rating) VALUES (?, ?, ?, ?, ?)',
        sample_attractions
    )
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

def create_spaces_app():
    """Create Flask app configured for Hugging Face Spaces"""
    # Setup SQLite database for demo
    db_path = setup_sqlite_database()
    
    # Set environment variables for Spaces deployment
    os.environ['FLASK_ENV'] = 'huggingface'
    os.environ['SECRET_KEY'] = 'huggingface-spaces-demo-key-change-in-production'
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

    # Import and create the main app
    from src.app import create_app, db
    config_name = os.getenv('FLASK_ENV', 'huggingface')
    app = create_app(config_name)

    # Create all database tables
    with app.app_context():
        db.create_all()

    # Override the home route for Spaces to provide a clear entry point message
    @app.route('/')
    def spaces_home():
        return jsonify({
            "message": "🇹🇭 PaiNaiDee Backend API is running on Hugging Face Spaces!",
            "description": "The full-featured Thai Tourism API is now active.",
            "api_base": "/api",
            "github": "https://github.com/athipan1/PaiNaiDee_Backend",
            "note": "This deployment uses a SQLite database."
        })

    # Add a health check endpoint required by the Dockerfile
    @app.route('/health')
    def health_check():
        # You could add a database check here if needed, e.g., db.session.query(User).first()
        return jsonify({"status": "healthy", "platform": "huggingface-spaces", "database": "sqlite"})
        
    return app

# Create the app instance for Hugging Face Spaces
app = create_spaces_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # Hugging Face Spaces default port
    app.run(host="0.0.0.0", port=port, debug=False)