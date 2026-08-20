"""projects can be published, or kept to their members

Reading a project used to require nothing beyond being signed in: any account
could read any project by id, and the open board listed every project that was
not cancelled. That was deliberate -- the product is about publishing a board to
attract collaborators -- but it was implicit, so there was no way to keep a board
to yourself.

`visibility` makes it explicit. PUBLIC is listed on the open board and readable
by any signed-in user; PRIVATE is readable only by the owner and the
collaborators, and a PRIVATE project answers 404 rather than 403 to everyone
else, so its existence does not leak either.

The default is PRIVATE, and the `server_default` matches: publishing is an act,
not the state a project starts in. Existing rows therefore become PRIVATE, which
is the conservative direction -- nothing that was hidden becomes visible.

Revision ID: b8580a18e189
Revises: 2df0758c479c
Create Date: 2026-08-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8580a18e189"
down_revision: Union[str, Sequence[str], None] = "2df0758c479c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "visibility",
            sa.String(length=20),
            server_default="PRIVATE",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("projects", "visibility")
