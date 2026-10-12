"""unique project tag

Revision ID: e5b8d2f4a6c1
Revises: d4a7c9e2f1b3
Create Date: 2026-10-11 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e5b8d2f4a6c1'
down_revision: Union[str, Sequence[str], None] = 'd4a7c9e2f1b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "DELETE FROM project_tags a USING project_tags b "
        "WHERE a.id > b.id AND a.id_project = b.id_project AND a.tag = b.tag"
    )
    op.create_unique_constraint('uq_project_tags_project_tag', 'project_tags', ['id_project', 'tag'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_project_tags_project_tag', 'project_tags', type_='unique')
