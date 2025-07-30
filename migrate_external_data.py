"""
Migration script to add external data tracking fields to attractions table

Adds fields to track external data sources, update timestamps, and data versions.
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.models import db
from sqlalchemy import text


def add_external_data_tracking_fields():
    """Add tracking fields for external data updates"""
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    
    with app.app_context():
        try:
            # Add new columns for external data tracking
            migrations = [
                # External data source identifier
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS external_id VARCHAR(255)",
                
                # Data source name (google_places, tat_api, tripadvisor, etc.)
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS data_source VARCHAR(100)",
                
                # Last update timestamp from external source
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS last_external_update TIMESTAMP",
                
                # Data version/hash for change detection
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS data_version VARCHAR(100)",
                
                # Creation timestamp for new attractions
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                
                # Last update timestamp for any changes
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                
                # Flag to indicate if data came from external source
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS is_external_data BOOLEAN DEFAULT FALSE",
                
                # JSON field for storing original external data
                "ALTER TABLE attractions ADD COLUMN IF NOT EXISTS external_data_raw JSONB"
            ]
            
            for migration in migrations:
                print(f"Executing: {migration}")
                db.session.execute(text(migration))
            
            # Add indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_attractions_external_id ON attractions(external_id)",
                "CREATE INDEX IF NOT EXISTS idx_attractions_data_source ON attractions(data_source)",
                "CREATE INDEX IF NOT EXISTS idx_attractions_last_external_update ON attractions(last_external_update)",
                "CREATE INDEX IF NOT EXISTS idx_attractions_created_at ON attractions(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_attractions_updated_at ON attractions(updated_at)",
                "CREATE INDEX IF NOT EXISTS idx_attractions_is_external_data ON attractions(is_external_data)"
            ]
            
            for index in indexes:
                print(f"Creating index: {index}")
                db.session.execute(text(index))
            
            # Create trigger to automatically update updated_at timestamp
            trigger_sql = """
            CREATE OR REPLACE FUNCTION update_modified_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            DROP TRIGGER IF EXISTS update_attractions_modtime ON attractions;
            CREATE TRIGGER update_attractions_modtime 
                BEFORE UPDATE ON attractions 
                FOR EACH ROW EXECUTE FUNCTION update_modified_column();
            """
            
            print("Creating trigger for automatic timestamp updates")
            db.session.execute(text(trigger_sql))
            
            # Update existing attractions to set default values
            update_existing = """
            UPDATE attractions 
            SET 
                created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
                updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP),
                is_external_data = COALESCE(is_external_data, FALSE)
            WHERE created_at IS NULL OR updated_at IS NULL OR is_external_data IS NULL
            """
            
            print("Updating existing attractions with default values")
            db.session.execute(text(update_existing))
            
            db.session.commit()
            print("✅ External data tracking fields added successfully!")
            
            # Verify the changes
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'attractions' 
                AND column_name IN (
                    'external_id', 'data_source', 'last_external_update', 
                    'data_version', 'created_at', 'updated_at', 
                    'is_external_data', 'external_data_raw'
                )
                ORDER BY column_name
            """))
            
            print("\n✅ Added columns:")
            for row in result:
                print(f"  - {row[0]} ({row[1]}, nullable: {row[2]})")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding external data tracking fields: {e}")
            return False
    
    return True


def create_external_data_history_table():
    """Create table for tracking external data update history"""
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    
    with app.app_context():
        try:
            # Create external data update history table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS external_data_updates (
                id SERIAL PRIMARY KEY,
                source_name VARCHAR(100) NOT NULL,
                update_type VARCHAR(50) NOT NULL, -- 'manual', 'scheduled', 'initial'
                started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
                total_processed INTEGER DEFAULT 0,
                new_created INTEGER DEFAULT 0,
                existing_updated INTEGER DEFAULT 0,
                errors_count INTEGER DEFAULT 0,
                error_messages TEXT[],
                parameters JSONB,
                result_summary JSONB,
                created_by INTEGER, -- User ID who triggered the update
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            );
            """
            
            print("Creating external_data_updates table")
            db.session.execute(text(create_table_sql))
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_external_data_updates_source ON external_data_updates(source_name)",
                "CREATE INDEX IF NOT EXISTS idx_external_data_updates_status ON external_data_updates(status)",
                "CREATE INDEX IF NOT EXISTS idx_external_data_updates_started_at ON external_data_updates(started_at)",
                "CREATE INDEX IF NOT EXISTS idx_external_data_updates_created_by ON external_data_updates(created_by)"
            ]
            
            for index in indexes:
                print(f"Creating index: {index}")
                db.session.execute(text(index))
            
            db.session.commit()
            print("✅ External data updates history table created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating external data history table: {e}")
            return False
    
    return True


def create_province_coverage_view():
    """Create view for province coverage analysis"""
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    
    with app.app_context():
        try:
            # Create view for province coverage analysis
            view_sql = """
            CREATE OR REPLACE VIEW province_coverage AS
            WITH thai_provinces AS (
                SELECT unnest(ARRAY[
                    'กรุงเทพมหานคร', 'กระบี่', 'กาญจนบุรี', 'กาฬสินธุ์', 'กำแพงเพชร',
                    'ขอนแก่น', 'จันทบุรี', 'ฉะเชิงเทรา', 'ชลบุรี', 'ชัยนาท', 'ชัยภูมิ',
                    'ชุมพร', 'เชียงราย', 'เชียงใหม่', 'ตรัง', 'ตราด', 'ตาก', 'นครนายก',
                    'นครปฐม', 'นครพนม', 'นครราชสีมา', 'นครศรีธรรมราช', 'นครสวรรค์',
                    'นนทบุรี', 'นราธิวาส', 'น่าน', 'บึงกาฬ', 'บุรีรัมย์', 'ปทุมธานี',
                    'ประจวบคีรีขันธ์', 'ปราจีนบุรี', 'ปัตตานี', 'พระนครศรีอยุธยา',
                    'พังงา', 'พัทลุง', 'พิจิตร', 'พิษณุโลก', 'เพชรบุรี', 'เพชรบูรณ์',
                    'แพร่', 'ภูเก็ต', 'มหาสารคาม', 'มุกดาหาร', 'แม่ฮ่องสอน', 'ยโสธร',
                    'ยะลา', 'ร้อยเอ็ด', 'ระนอง', 'ระยอง', 'ราชบุรี', 'ลพบุรี', 'ลำปาง',
                    'ลำพูน', 'เลย', 'ศรีสะเกษ', 'สกลนคร', 'สงขลา', 'สตูล', 'สมุทรปราการ',
                    'สมุทรสงคราม', 'สมุทรสาคร', 'สระแก้ว', 'สระบุรี', 'สิงห์บุรี',
                    'สุโขทัย', 'สุพรรณบุรี', 'สุราษฎร์ธานี', 'สุรินทร์', 'หนองคาย',
                    'หนองบัวลำภู', 'อ่างทอง', 'อำนาจเจริญ', 'อุดรธานี', 'อุตรดิตถ์',
                    'อุทัยธานี', 'อุบลราชธานี'
                ]) AS province_name
            ),
            attraction_counts AS (
                SELECT 
                    province,
                    COUNT(*) as total_attractions,
                    COUNT(CASE WHEN is_external_data = TRUE THEN 1 END) as external_attractions,
                    COUNT(CASE WHEN main_image_url IS NOT NULL AND main_image_url != '' THEN 1 END) as attractions_with_images,
                    COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL 
                              AND latitude != 0 AND longitude != 0 THEN 1 END) as attractions_with_coordinates,
                    MAX(updated_at) as last_updated
                FROM attractions 
                WHERE province IS NOT NULL AND province != ''
                GROUP BY province
            )
            SELECT 
                tp.province_name,
                COALESCE(ac.total_attractions, 0) as total_attractions,
                COALESCE(ac.external_attractions, 0) as external_attractions,
                COALESCE(ac.attractions_with_images, 0) as attractions_with_images,
                COALESCE(ac.attractions_with_coordinates, 0) as attractions_with_coordinates,
                ac.last_updated,
                CASE WHEN ac.total_attractions > 0 THEN TRUE ELSE FALSE END as has_data
            FROM thai_provinces tp
            LEFT JOIN attraction_counts ac ON tp.province_name = ac.province
            ORDER BY tp.province_name;
            """
            
            print("Creating province_coverage view")
            db.session.execute(text(view_sql))
            
            db.session.commit()
            print("✅ Province coverage view created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating province coverage view: {e}")
            return False
    
    return True


if __name__ == "__main__":
    print("🚀 Running external data tracking migration...")
    
    # Run migrations
    success1 = add_external_data_tracking_fields()
    success2 = create_external_data_history_table()
    success3 = create_province_coverage_view()
    
    if success1 and success2 and success3:
        print("✅ All external data migrations completed successfully!")
    else:
        print("❌ Some migrations failed!")
        sys.exit(1)