"""Add Phase 1 models: locations, posts, post_media

Revision ID: 001_phase1_models
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_phase1_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    # PostGIS is optional - will be handled gracefully if not available
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS "postgis";')
    except Exception:
        pass  # PostGIS not available, will use lat/lng columns
    
    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('province', sa.Text(), nullable=True),
        sa.Column('aliases', postgresql.ARRAY(sa.Text()), server_default='{}'),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('popularity_score', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create posts table
    op.create_table(
        'posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), server_default='{}'),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('like_count', sa.Integer(), server_default='0'),
        sa.Column('comment_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'])
    )
    
    # Create post_media table
    op.create_table(
        'post_media',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('media_type', sa.String(20), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('thumb_url', sa.Text(), nullable=True),
        sa.Column('ordering', sa.Integer(), server_default='0'),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.CheckConstraint("media_type IN ('image', 'video')", name='check_media_type')
    )
    
    # Create indexes for performance
    # Trigram index for fuzzy search on location names
    op.execute('CREATE INDEX idx_locations_name_trgm ON locations USING gin (name gin_trgm_ops);')
    
    # GIN indexes for array columns
    op.create_index('idx_locations_aliases', 'locations', ['aliases'], postgresql_using='gin')
    op.create_index('idx_posts_tags', 'posts', ['tags'], postgresql_using='gin')
    
    # Standard indexes
    op.create_index('idx_posts_location_id', 'posts', ['location_id'])
    op.create_index('idx_posts_created_at', 'posts', ['created_at'])
    op.create_index('idx_posts_like_count', 'posts', ['like_count'])
    op.create_index('idx_posts_user_id', 'posts', ['user_id'])
    op.create_index('idx_post_media_post_id', 'post_media', ['post_id'])
    
    # Geographic indexes if PostGIS is available
    try:
        op.execute('CREATE INDEX idx_locations_geo ON locations USING gist (ST_Point(lng, lat));')
        op.execute('CREATE INDEX idx_posts_geo ON posts USING gist (ST_Point(lng, lat)) WHERE lat IS NOT NULL AND lng IS NOT NULL;')
    except Exception:
        # PostGIS not available, create regular indexes for lat/lng
        op.create_index('idx_locations_lat_lng', 'locations', ['lat', 'lng'])
        op.create_index('idx_posts_lat_lng', 'posts', ['lat', 'lng'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('post_media')
    op.drop_table('posts')
    op.drop_table('locations')