"""add_engagement_tables_and_constraints

Revision ID: 7c6b83ddd731
Revises: 42cd6ad83f29
Create Date: 2025-09-16 00:30:09.044591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c6b83ddd731'
down_revision: Union[str, None] = '42cd6ad83f29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create post_likes table
    op.create_table(
        'post_likes',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('post_id', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('post_id', 'user_id', name='uq_post_likes_post_user'),
    )
    
    # Create post_comments table
    op.create_table(
        'post_comments',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('post_id', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for performance
    op.create_index('idx_post_likes_post_id', 'post_likes', ['post_id'])
    op.create_index('idx_post_likes_user_id', 'post_likes', ['user_id'])
    op.create_index('idx_post_comments_post_id', 'post_comments', ['post_id'])
    op.create_index('idx_post_comments_user_id', 'post_comments', ['user_id'])
    op.create_index('idx_post_comments_created_at', 'post_comments', ['created_at'])


def downgrade() -> None:
    op.drop_table('post_comments')
    op.drop_table('post_likes')
