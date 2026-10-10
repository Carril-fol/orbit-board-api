"""unique username

Revision ID: b8e4f1a2c3d6
Revises: 7a3c5e9b1d2f
Create Date: 2026-10-09 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b8e4f1a2c3d6'
down_revision: Union[str, Sequence[str], None] = '7a3c5e9b1d2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('users_username_key', 'users', ['username'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('users_username_key', 'users', type_='unique')
