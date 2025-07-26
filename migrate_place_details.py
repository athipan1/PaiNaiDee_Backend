"""
Migration script for creating the PlaceDetails table.
This script adds the PlaceDetails table to support additional place information.
"""

import os
import sys
from sqlalchemy import text

# Add src directory to path to import our models
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app
from src.models import db


def create_place_details_table():
    """Create the PlaceDetails table as specified in requirements"""
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    
    with app.app_context():
        # SQL for creating the PlaceDetails table as specified in requirements
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS place_details (
            id SERIAL PRIMARY KEY,
            place_id INT REFERENCES attractions(id) ON DELETE CASCADE,
            description TEXT,
            link TEXT
        );
        """
        
        try:
            # Execute the SQL
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ PlaceDetails table created successfully.")
            
            # Verify the table was created
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'place_details'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            if columns:
                print("\n📋 Table structure:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
            else:
                print("⚠️  Table structure verification failed")
                
        except Exception as e:
            print(f"❌ Error creating PlaceDetails table: {e}")
            db.session.rollback()
            raise


def verify_foreign_key():
    """Verify the foreign key relationship works correctly"""
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    
    with app.app_context():
        try:
            # Check if foreign key constraint exists
            result = db.session.execute(text("""
                SELECT constraint_name 
                FROM information_schema.referential_constraints 
                WHERE constraint_schema = current_schema()
                AND referenced_table_name = 'attractions'
                AND table_name = 'place_details';
            """))
            
            constraints = result.fetchall()
            if constraints:
                print("✅ Foreign key constraint verified")
            else:
                print("⚠️  Foreign key constraint not found (this may be normal for SQLite)")
                
        except Exception as e:
            print(f"⚠️  Foreign key verification failed: {e}")


if __name__ == "__main__":
    print("🚀 Creating PlaceDetails table migration...")
    create_place_details_table()
    verify_foreign_key()
    print("\n✨ Migration completed!")
    print("\nTable supports the following operations:")
    print("  - GET /api/places/:id - Get place with optional details")
    print("  - POST /api/places/:id/details - Add place details")
    print("  - PUT /api/places/:id/details - Update place details")
    print("  - DELETE /api/places/:id/details - Delete place details")