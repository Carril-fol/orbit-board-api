"""requests timestamps become timezone aware

`requests` was the last table left with naive timestamps: `comments` and
`project_invitations` already store `TIMESTAMPTZ`, so the API answered with an
offset for an invitation and without one for a request. The client could not
tell what zone the request dates were in.

The conversion reads the existing values as UTC, which is what they were:
`created_at` was written by Postgres' `now()`, and `review_at` was never
written at all -- `respond_request` only ever changed `status`, so the column
was NULL on every row. It is filled from now on, at the moment the owner
approves or declines.

Revision ID: a4c93f16d2b7
Revises: b8580a18e189
Create Date: 2026-08-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4c93f16d2b7"
down_revision: Union[str, Sequence[str], None] = "b8580a18e189"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "requests",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_server_default=sa.text("now()"),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "requests",
        "review_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="review_at AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    op.alter_column(
        "requests",
        "review_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="review_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "requests",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_server_default=sa.text("now()"),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
