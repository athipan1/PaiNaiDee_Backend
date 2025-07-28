"""
Database migration script to add API analytics table
Run this script to create the api_analytics table in your database
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.models import db

def create_analytics_table():
    """Create the API analytics table"""
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    
    with app.app_context():
        try:
            # Create the analytics table
            db.create_all()
            print("✅ API analytics table created successfully!")
            
            # Verify table exists
            inspector = db.inspect(db.engine)
            if 'api_analytics' in inspector.get_table_names():
                print("✅ api_analytics table verified in database")
            else:
                print("❌ api_analytics table not found in database")
                
        except Exception as e:
            print(f"❌ Error creating analytics table: {e}")
            return False
        
    return True

if __name__ == "__main__":
    print("🚀 Creating API analytics table...")
    success = create_analytics_table()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)