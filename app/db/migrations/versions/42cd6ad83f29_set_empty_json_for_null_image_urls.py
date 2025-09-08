"""Set empty json for null image_urls

Revision ID: 42cd6ad83f29
Revises: 001_phase1_models
Create Date: 2025-09-08 16:50:43.230484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42cd6ad83f29'
down_revision: Union[str, None] = '001_phase1_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE attractions SET image_urls = '{}' WHERE image_urls IS NULL OR image_urls = ''")


def downgrade() -> None:
    # This change is not easily reversible as we lose the information about which rows were NULL.
    # We will leave the downgrade empty.
    pass
