"""add REVOKED invitation status

Revision ID: 9c1d2e3f4a5b
Revises: 4f06831a6f75
Create Date: 2026-10-06 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9c1d2e3f4a5b'
down_revision: Union[str, Sequence[str], None] = '4f06831a6f75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Autogenerate does not detect new values of a native Postgres enum.
    op.execute("ALTER TYPE invitationstatus ADD VALUE IF NOT EXISTS 'REVOKED'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres cannot drop a value from an enum; revoked rows go back to REJECTED
    # and the value stays in the type, unused.
    op.execute("UPDATE project_invitations SET status = 'REJECTED' WHERE status = 'REVOKED'")
