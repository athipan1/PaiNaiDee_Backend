"""Add engagement tables for likes and comments

Revision ID: 002_add_engagement
Revises: 001_phase1_models
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '002_add_engagement'
down_revision = '001_phase1_models'
branch_labels = None
depends_on = None


def upgrade():
    """Add engagement tables for likes and comments"""
    
    # Create post_likes table
    op.create_table(
        'post_likes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('post_id', 'user_id', name='uq_post_user_like')
    )
    
    # Create post_comments table
    op.create_table(
        'post_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE')
    )
    
    # Create indexes for performance
    op.create_index('idx_post_likes_post_id', 'post_likes', ['post_id'])
    op.create_index('idx_post_likes_user_id', 'post_likes', ['user_id'])
    op.create_index('idx_post_comments_post_id', 'post_comments', ['post_id'])
    op.create_index('idx_post_comments_user_id', 'post_comments', ['user_id'])
    op.create_index('idx_post_comments_created_at', 'post_comments', ['created_at'])


def downgrade():
    """Remove engagement tables"""
    op.drop_index('idx_post_comments_created_at')
    op.drop_index('idx_post_comments_user_id')
    op.drop_index('idx_post_comments_post_id')
    op.drop_index('idx_post_likes_user_id')
    op.drop_index('idx_post_likes_post_id')
    op.drop_table('post_comments')
    op.drop_table('post_likes')