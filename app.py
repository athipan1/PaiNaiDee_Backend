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
    
    # Try to create the main app, fallback to simple app if it fails
    try:
        # Set environment variables for Spaces deployment
        os.environ['FLASK_ENV'] = 'production'
        os.environ['SECRET_KEY'] = 'huggingface-spaces-demo-key-change-in-production'
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        os.environ['DB_HOST'] = ''
        os.environ['DB_NAME'] = ''
        os.environ['DB_USER'] = ''
        os.environ['DB_PASSWORD'] = ''
        os.environ['DB_PORT'] = ''
        
        # Try to import and create the main app
        from src.app import create_app
        app = create_app('production')
        
        # Override the home route for Spaces
        @app.route('/')
        def spaces_home():
            return jsonify({
                "message": "🇹🇭 PaiNaiDee Backend API is running on Hugging Face Spaces!",
                "description": "Thai Tourism API - Where to go in Thailand",
                "api_base": "/api",
                "endpoints": {
                    "attractions": "/api/attractions",
                    "search": "/api/search",
                    "auth": "/api/auth",
                    "documentation": "See GitHub README for complete API documentation"
                },
                "github": "https://github.com/athipan1/PaiNaiDee_Backend",
                "note": "This is a demo deployment with SQLite database. For production use PostgreSQL."
            })
        
        @app.route('/health')
        def health_check():
            return jsonify({"status": "healthy", "platform": "huggingface-spaces", "database": "sqlite"})
            
        return app
        
    except Exception as init_error:
        # Create a simple fallback Flask app with basic API endpoints
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'huggingface-spaces-fallback-key'
        
        @app.route('/')
        def fallback_home():
            return jsonify({
                "message": "🇹🇭 PaiNaiDee Backend API (Fallback Mode)",
                "description": "Thai Tourism API - Basic demo with sample data",
                "status": "running_in_fallback_mode",
                "reason": "Main app initialization failed",
                "available_endpoints": {
                    "attractions": "/api/attractions",
                    "attraction_by_id": "/api/attractions/<id>",
                    "search": "/api/search",
                    "health": "/health"
                },
                "github": "https://github.com/athipan1/PaiNaiDee_Backend",
                "note": "This is a simplified version due to initialization issues."
            })
        
        @app.route('/health')
        def fallback_health():
            return jsonify({
                "status": "healthy", 
                "platform": "huggingface-spaces", 
                "mode": "fallback",
                "database": "sqlite"
            })
        
        @app.route('/api/attractions')
        def get_attractions():
            """Get all attractions from SQLite database"""
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attractions")
                rows = cursor.fetchall()
                conn.close()
                
                attractions = []
                for row in rows:
                    attractions.append({
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "province": row[3],
                        "category": row[4],
                        "rating": row[5],
                        "created_at": row[6]
                    })
                
                return jsonify({
                    "success": True,
                    "attractions": attractions,
                    "total": len(attractions),
                    "message": "Attractions retrieved successfully"
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to retrieve attractions"
                }), 500
        
        @app.route('/api/attractions/<int:attraction_id>')
        def get_attraction(attraction_id):
            """Get specific attraction by ID"""
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attractions WHERE id = ?", (attraction_id,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    attraction = {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "province": row[3],
                        "category": row[4],
                        "rating": row[5],
                        "created_at": row[6]
                    }
                    return jsonify({
                        "success": True,
                        "attraction": attraction,
                        "message": "Attraction found"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": "Attraction not found"
                    }), 404
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to retrieve attraction"
                }), 500
        
        @app.route('/api/search')
        def search_attractions():
            """Search attractions by name or category"""
            from flask import request
            try:
                query = request.args.get('q', '')
                if not query:
                    return jsonify({
                        "success": False,
                        "message": "Query parameter 'q' is required"
                    }), 400
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM attractions WHERE name LIKE ? OR category LIKE ? OR description LIKE ?", 
                    (f'%{query}%', f'%{query}%', f'%{query}%')
                )
                rows = cursor.fetchall()
                conn.close()
                
                attractions = []
                for row in rows:
                    attractions.append({
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "province": row[3],
                        "category": row[4],
                        "rating": row[5],
                        "created_at": row[6]
                    })
                
                return jsonify({
                    "success": True,
                    "attractions": attractions,
                    "total": len(attractions),
                    "query": query,
                    "message": f"Found {len(attractions)} attractions matching '{query}'"
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "message": "Search failed"
                }), 500
        
        # Add CORS support for fallback app
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        return app

# Create the app instance for Hugging Face Spaces
app = create_spaces_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # Hugging Face Spaces default port
    app.run(host="0.0.0.0", port=port, debug=False)