"""
Database migration script for PaiNaiDee Admin Video Management System
This script adds the necessary columns and enables Row-Level Security (RLS)
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import db, User, VideoPost
from src.app import create_app


def create_admin_user(app):
    """Create a default admin user for testing"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email="admin@painaidee.com").first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(
                username="admin",
                email="admin@painaidee.com",
                password=generate_password_hash("admin123456"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Created default admin user: admin@painaidee.com / admin123456")
        else:
            print("ℹ️  Admin user already exists")


def setup_rls_policies(app):
    """Set up Row-Level Security policies for PostgreSQL"""
    with app.app_context():
        try:
            # Check if we're using PostgreSQL
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql' not in database_url.lower():
                print("ℹ️  Skipping RLS setup (not using PostgreSQL)")
                return
                
            # Enable RLS on video_posts table
            db.session.execute(db.text("ALTER TABLE video_posts ENABLE ROW LEVEL SECURITY;"))
            print("✅ Enabled RLS on video_posts table")
            
            # Drop existing policies if they exist
            try:
                db.session.execute(db.text("DROP POLICY IF EXISTS admin_video_policy ON video_posts;"))
            except:
                pass
            
            # Create RLS policy: admins can only see/modify their own videos
            policy_sql = """
            CREATE POLICY admin_video_policy ON video_posts
            FOR ALL
            USING (user_id = CAST(current_setting('app.current_user_id', true) AS INTEGER))
            WITH CHECK (user_id = CAST(current_setting('app.current_user_id', true) AS INTEGER));
            """
            
            db.session.execute(db.text(policy_sql))
            print("✅ Created RLS policy for video_posts")
            
            db.session.commit()
            
        except Exception as e:
            print(f"⚠️  Could not set up RLS policies: {e}")
            db.session.rollback()


def migrate_existing_data(app):
    """Migrate existing data to new schema"""
    with app.app_context():
        try:
            # Update any existing users without email to have a placeholder email
            users_without_email = User.query.filter_by(email=None).all()
            for user in users_without_email:
                user.email = f"{user.username}@painaidee-placeholder.com"
                print(f"✅ Added placeholder email for user: {user.username}")
            
            # Update any existing video posts without title to have a default title
            videos_without_title = VideoPost.query.filter_by(title=None).all()
            for video in videos_without_title:
                video.title = video.caption[:50] if video.caption else f"Video {video.id}"
                print(f"✅ Added default title for video: {video.id}")
            
            db.session.commit()
            print("✅ Migrated existing data")
            
        except Exception as e:
            print(f"❌ Error migrating existing data: {e}")
            db.session.rollback()


def run_migration():
    """Run the complete migration"""
    print("🚀 Starting PaiNaiDee Admin Video System Migration...")
    
    # Create Flask app with testing config for SQLite
    app = create_app("testing")
    
    with app.app_context():
        try:
            # Create all tables with new schema
            db.create_all()
            print("✅ Created/updated database tables")
            
            # Migrate existing data
            migrate_existing_data(app)
            
            # Create default admin user
            create_admin_user(app)
            
            # Set up RLS policies (PostgreSQL only)
            setup_rls_policies(app)
            
            print("🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Test admin login: POST /api/auth/admin/login")
            print("   Email: admin@painaidee.com")
            print("   Password: admin123456")
            print("2. Upload videos: POST /api/admin/videos/upload")
            print("3. View admin videos: GET /api/admin/videos")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True


if __name__ == "__main__":
    success = run_migration()
    if not success:
        sys.exit(1)