"""make collaborator role nullable and drop the OWNER marker

Ownership moved to project.owner_id as the single source of truth. The role
column goes back to describing what a collaborator does on the project
(backend, devops, ...), so the "OWNER" value written at project creation no
longer means anything and is cleared.

Revision ID: b7c41d9e0a52
Revises: db05b324166b
Create Date: 2026-08-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c41d9e0a52"
down_revision: Union[str, None] = "db05b324166b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "collaborators",
        "role",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.execute("UPDATE collaborators SET role = NULL WHERE role = 'OWNER'")


def downgrade() -> None:
    op.execute(
        """
        UPDATE collaborators AS c
        SET role = 'OWNER'
        FROM projects AS p
        WHERE c.id_project = p.id
          AND c.id_user = p.owner_id
          AND c.role IS NULL
        """
    )
    op.execute("UPDATE collaborators SET role = '' WHERE role IS NULL")
    op.alter_column(
        "collaborators",
        "role",
        existing_type=sa.String(length=100),
        nullable=False,
    )
