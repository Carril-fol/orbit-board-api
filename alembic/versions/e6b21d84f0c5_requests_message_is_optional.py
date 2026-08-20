"""a join request no longer needs a message

The API has always advertised the message as optional: `message` is
`Optional[str] = None` on the input schema, and that is what `/docs` publishes.
The column said otherwise, so posting a request without one reached Postgres as
a NULL and came back as an unhandled 500 -- a NotNullViolationError, with no
exception handler to turn it into anything a client could read.

The contract wins over the column. Asking to join a public board is the kind of
thing that should not require writing a paragraph first, and every existing row
already has a message, so nothing is lost by relaxing the constraint.

Revision ID: e6b21d84f0c5
Revises: a4c93f16d2b7
Create Date: 2026-08-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e6b21d84f0c5"
down_revision: Union[str, Sequence[str], None] = "a4c93f16d2b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "requests",
        "message",
        existing_type=sa.String(length=255),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("UPDATE requests SET message = '' WHERE message IS NULL")
    op.alter_column(
        "requests",
        "message",
        existing_type=sa.String(length=255),
        nullable=False,
    )
