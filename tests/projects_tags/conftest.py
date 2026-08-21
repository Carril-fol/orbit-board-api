import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from projects_tags.models.project_tag_model import ProjectTag
from projects_tags.repositories.project_tag_repository import ProjectTagRepository

@pytest.fixture
def tag_data():
    return {"tag": "URGENT"}

@pytest.fixture
def project_tag_repo(db_session: AsyncSession):
    return ProjectTagRepository(db_session)

@pytest.fixture
async def project_tag_created(authenticated_client, project_created, db_session, tag_data):
    await authenticated_client.post(
        f"/projects/api/v1/{project_created.id}/tags",
        json=tag_data,
    )
    stmt = select(ProjectTag).where(ProjectTag.id_project == project_created.id)
    result = await db_session.execute(stmt)
    return result.scalars().first()
