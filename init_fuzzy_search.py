"""
Database initialization script for fuzzy search setup
This script sets up PostgreSQL with pg_trgm extension for enhanced fuzzy search capabilities
"""

from src.models import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def init_fuzzy_search_extensions():
    """Initialize PostgreSQL extensions for fuzzy search"""
    try:
        # Check if running on SQLite (testing environment)
        if 'sqlite' in str(db.engine.url):
            logger.info("SQLite detected - skipping PostgreSQL extensions")
            return False
        
        # Enable pg_trgm extension for trigram matching
        db.session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        logger.info("pg_trgm extension enabled")
        
        # Enable unaccent extension for handling accented characters
        try:
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
            logger.info("unaccent extension enabled")
        except Exception as e:
            logger.warning(f"unaccent extension not available: {e}")
        
        # Create GIN indexes for better fuzzy search performance
        try:
            # Index for attraction names
            db.session.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attractions_name_gin 
                ON attractions USING gin (name gin_trgm_ops);
            """))
            
            # Index for descriptions
            db.session.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attractions_description_gin 
                ON attractions USING gin (description gin_trgm_ops);
            """))
            
            # Index for provinces
            db.session.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attractions_province_gin 
                ON attractions USING gin (province gin_trgm_ops);
            """))
            
            logger.info("GIN indexes created for fuzzy search")
            
        except Exception as e:
            logger.warning(f"Could not create GIN indexes: {e}")
        
        db.session.commit()
        logger.info("Fuzzy search extensions initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing fuzzy search extensions: {e}")
        db.session.rollback()
        return False


def create_fuzzy_search_functions():
    """Create custom PostgreSQL functions for advanced fuzzy search"""
    try:
        if 'sqlite' in str(db.engine.url):
            return False
        
        # Create a function for fuzzy search with similarity threshold
        db.session.execute(text("""
            CREATE OR REPLACE FUNCTION fuzzy_search_attractions(
                search_query TEXT,
                similarity_threshold REAL DEFAULT 0.3
            )
            RETURNS TABLE (
                id INTEGER,
                name VARCHAR(255),
                description TEXT,
                province VARCHAR(100),
                similarity_score REAL
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    a.id,
                    a.name,
                    a.description,
                    a.province,
                    GREATEST(
                        similarity(a.name, search_query),
                        similarity(a.description, search_query),
                        similarity(a.province, search_query)
                    ) as similarity_score
                FROM attractions a
                WHERE 
                    similarity(a.name, search_query) > similarity_threshold OR
                    similarity(a.description, search_query) > similarity_threshold OR
                    similarity(a.province, search_query) > similarity_threshold
                ORDER BY similarity_score DESC;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        db.session.commit()
        logger.info("Fuzzy search functions created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating fuzzy search functions: {e}")
        db.session.rollback()
        return False


if __name__ == "__main__":
    from src.app import create_app
    
    app = create_app("development")
    with app.app_context():
        # Initialize database tables
        db.create_all()
        
        # Setup fuzzy search extensions
        init_fuzzy_search_extensions()
        create_fuzzy_search_functions()
        
        print("Database initialized with fuzzy search capabilities")