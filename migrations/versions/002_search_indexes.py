"""Add search indexes and pg_trgm extension

Revision ID: 002_search_indexes
Revises: 001_initial_tables
Create Date: 2024-12-15 12:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_search_indexes'
down_revision = '001_initial_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Enable pg_trgm extension for trigram similarity searches
    # Note: This requires superuser privileges in PostgreSQL
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    except Exception:
        # If extension creation fails (e.g., in SQLite for testing), continue
        pass
    
    # Add search indexes for attractions table
    # GIN index for full-text search on name and description
    try:
        op.execute('''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attractions_name_gin
            ON attractions USING gin (name gin_trgm_ops);
        ''')
    except Exception:
        # Fallback for databases that don't support GIN indexes
        op.create_index('idx_attractions_name_search', 'attractions', ['name'])
    
    try:
        op.execute('''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attractions_description_gin
            ON attractions USING gin (description gin_trgm_ops);
        ''')
    except Exception:
        pass
    
    # GIST index for geospatial queries (if PostGIS is available)
    try:
        op.execute('''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attractions_location_gist
            ON attractions USING gist (ll_to_earth(latitude, longitude));
        ''')
    except Exception:
        # Fallback: regular index on latitude and longitude
        op.create_index('idx_attractions_latitude', 'attractions', ['latitude'])
        op.create_index('idx_attractions_longitude', 'attractions', ['longitude'])
    
    # Add indexes for search performance on other searchable fields
    op.create_index('idx_attractions_name_lower', 'attractions', [sa.text('lower(name)')])
    op.create_index('idx_attractions_category_lower', 'attractions', [sa.text('lower(category)')])
    
    # Add composite indexes for common search patterns
    op.create_index('idx_attractions_province_category', 'attractions', ['province', 'category'])
    op.create_index('idx_attractions_category_rating', 'attractions', ['category', 'rating'])
    
    # Search indexes for video posts
    try:
        op.execute('''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_video_posts_title_gin
            ON video_posts USING gin (title gin_trgm_ops);
        ''')
    except Exception:
        op.create_index('idx_video_posts_title_search', 'video_posts', ['title'])
    
    try:
        op.execute('''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_video_posts_tags_gin
            ON video_posts USING gin (tags gin_trgm_ops);
        ''')
    except Exception:
        op.create_index('idx_video_posts_tags_search', 'video_posts', ['tags'])
    
    # Additional performance indexes
    op.create_index('idx_video_posts_created_at', 'video_posts', ['created_at'])
    op.create_index('idx_video_posts_views', 'video_posts', ['views'])
    op.create_index('idx_video_posts_attraction_id', 'video_posts', ['attraction_id'])
    
    # Add search-related columns for future use (optional)
    # These could be used to store pre-computed search vectors or normalized text
    try:
        op.add_column('attractions', sa.Column('search_vector', sa.Text(), nullable=True))
        op.add_column('attractions', sa.Column('normalized_name', sa.String(length=255), nullable=True))
    except Exception:
        # Column might already exist or database doesn't support this operation
        pass


def downgrade():
    # Remove search-related columns
    try:
        op.drop_column('attractions', 'normalized_name')
        op.drop_column('attractions', 'search_vector')
    except Exception:
        pass
    
    # Drop search indexes
    indexes_to_drop = [
        'idx_attractions_name_gin',
        'idx_attractions_description_gin',
        'idx_attractions_location_gist',
        'idx_attractions_name_search',
        'idx_attractions_name_lower',
        'idx_attractions_category_lower',
        'idx_attractions_province_category',
        'idx_attractions_category_rating',
        'idx_attractions_latitude',
        'idx_attractions_longitude',
        'idx_video_posts_title_gin',
        'idx_video_posts_title_search',
        'idx_video_posts_tags_gin',
        'idx_video_posts_tags_search',
        'idx_video_posts_created_at',
        'idx_video_posts_views',
        'idx_video_posts_attraction_id',
    ]
    
    for index_name in indexes_to_drop:
        try:
            op.drop_index(index_name)
        except Exception:
            # Index might not exist or already dropped
            pass
    
    # Note: We don't drop the pg_trgm extension as it might be used by other applications