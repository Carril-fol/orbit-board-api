"""one collaborator row per (user, project)

Nothing stopped the same user from being added to a project twice. A duplicate
row double-counts against the project's max_collaborators and shows the person
twice in the collaborator list, so the pair becomes unique.

The upgrade deduplicates first: it keeps the earliest row of each pair (lowest
id, which is also the original join) and drops the rest, otherwise the
constraint cannot be created on a table that already violates it.

Revision ID: c1a7e4b90d33
Revises: 23e489df8b9f
Create Date: 2026-08-15

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c1a7e4b90d33"
down_revision: Union[str, None] = "23e489df8b9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CONSTRAINT_NAME = "uq_collaborators_user_project"


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM collaborators
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM collaborators
            GROUP BY id_user, id_project
        )
        """
    )
    op.create_unique_constraint(
        CONSTRAINT_NAME,
        "collaborators",
        ["id_user", "id_project"],
    )


def downgrade() -> None:
    # The deleted duplicates are not recoverable, so this only lifts the rule.
    op.drop_constraint(CONSTRAINT_NAME, "collaborators", type_="unique")
