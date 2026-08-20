"""audit log project scope, and comment timestamps that actually work

Two unrelated fixes that landed together.

`audit_logs` gains `project_id`. Without it the trail is only readable by
entity id, which forces the reader to already know what they are looking for,
and forces the audit module to resolve every entity type back to its project
just to authorize the read. Every auditable action already happens inside a
project, so the column is NOT NULL: an audit row nobody can attribute to a
project is a row nobody can be authorized to read. It is a plain integer and
deliberately not a foreign key, matching `user_id` -- audit rows have to
outlive the project they describe, and an FK would make any hard delete of a
project fail. Adding a NOT NULL column assumes the table is empty, which it is
here; on a populated table this fails loudly rather than backfilling every old
row with a project it does not belong to.

`comments.created_at` and `updated_at` move to TIMESTAMPTZ. They were declared
`DateTime` (naive) while the model fed them timezone-aware values, so asyncpg
rejected every insert and update -- creating or editing a comment returned 500.
The USING clause is explicit: the values that were stored were meant as UTC, so
they are reinterpreted as UTC rather than as the server's local timezone.

Revision ID: 2df0758c479c
Revises: c1a7e4b90d33
Create Date: 2026-08-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "2df0758c479c"
down_revision: Union[str, Sequence[str], None] = "c1a7e4b90d33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TIMESTAMP_COLUMNS = ("created_at", "updated_at")


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column("project_id", sa.Integer(), nullable=False),
    )

    for column in TIMESTAMP_COLUMNS:
        op.alter_column(
            "comments",
            column,
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )


def downgrade() -> None:
    for column in TIMESTAMP_COLUMNS:
        op.alter_column(
            "comments",
            column,
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )

    op.drop_column("audit_logs", "project_id")
