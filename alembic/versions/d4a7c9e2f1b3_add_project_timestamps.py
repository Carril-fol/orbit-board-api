"""add project timestamps

Revision ID: d4a7c9e2f1b3
Revises: b8e4f1a2c3d6
Create Date: 2026-10-09 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4a7c9e2f1b3'
down_revision: Union[str, Sequence[str], None] = 'b8e4f1a2c3d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('projects', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'updated_at')
    op.drop_column('projects', 'created_at')
