import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from projects.repositories.project_repository import ProjectRepository

@pytest.fixture
def project_repo(db_session: AsyncSession):
    return ProjectRepository(db_session)