"""Initial migration with existing tables

Revision ID: 001_initial_tables
Revises: 
Create Date: 2024-12-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Attractions table
    op.create_table('attractions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('province', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_email', sa.String(length=120), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Reviews table
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('place_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['place_id'], ['attractions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Rooms table
    op.create_table('rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('attraction_id', sa.Integer(), nullable=False),
        sa.Column('room_type', sa.String(length=100), nullable=False),
        sa.Column('price_per_night', sa.Float(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amenities', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['attraction_id'], ['attractions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Cars table
    op.create_table('cars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('attraction_id', sa.Integer(), nullable=False),
        sa.Column('car_model', sa.String(length=100), nullable=False),
        sa.Column('price_per_day', sa.Float(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('features', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['attraction_id'], ['attractions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Room bookings table
    op.create_table('room_bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('check_in_date', sa.Date(), nullable=False),
        sa.Column('check_out_date', sa.Date(), nullable=False),
        sa.Column('guests', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Car rentals table
    op.create_table('car_rentals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('car_id', sa.Integer(), nullable=False),
        sa.Column('rental_start_date', sa.Date(), nullable=False),
        sa.Column('rental_end_date', sa.Date(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Video posts table
    op.create_table('video_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('attraction_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['attraction_id'], ['attractions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # API analytics table
    op.create_table('api_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_size', sa.Integer(), nullable=True),
        sa.Column('response_size', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Data sources table
    op.create_table('data_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Manual updates table
    op.create_table('manual_updates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_source_id', sa.Integer(), nullable=False),
        sa.Column('update_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True),
        sa.Column('records_successful', sa.Integer(), nullable=True),
        sa.Column('records_failed', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['data_source_id'], ['data_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Scheduled updates table
    op.create_table('scheduled_updates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_source_id', sa.Integer(), nullable=False),
        sa.Column('cron_expression', sa.String(length=100), nullable=False),
        sa.Column('update_type', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('next_run', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['data_source_id'], ['data_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Basic indexes for performance
    op.create_index('idx_attractions_province', 'attractions', ['province'])
    op.create_index('idx_attractions_category', 'attractions', ['category'])
    op.create_index('idx_attractions_rating', 'attractions', ['rating'])
    op.create_index('idx_reviews_place_id', 'reviews', ['place_id'])
    op.create_index('idx_reviews_user_id', 'reviews', ['user_id'])
    op.create_index('idx_api_analytics_timestamp', 'api_analytics', ['timestamp'])
    op.create_index('idx_api_analytics_endpoint', 'api_analytics', ['endpoint'])


def downgrade():
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('scheduled_updates')
    op.drop_table('manual_updates')
    op.drop_table('data_sources')
    op.drop_table('api_analytics')
    op.drop_table('video_posts')
    op.drop_table('car_rentals')
    op.drop_table('room_bookings')
    op.drop_table('cars')
    op.drop_table('rooms')
    op.drop_table('reviews')
    op.drop_table('attractions')
    op.drop_table('users')