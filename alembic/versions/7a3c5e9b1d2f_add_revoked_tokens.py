"""add revoked tokens

Revision ID: 7a3c5e9b1d2f
Revises: 2e007e743a27
Create Date: 2026-10-08 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a3c5e9b1d2f'
down_revision: Union[str, Sequence[str], None] = '2e007e743a27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('revoked_tokens',
    sa.Column('jti', sa.String(length=36), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('jti')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('revoked_tokens')
