import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from projects.repositories.project_repository import ProjectRepository
from requests.repositories.requests_repository import RequestsRepository

PRIVATE_PROJECT_DATA = {
    "name": "Private project tests",
    "description": "Project description",
    "status": "PLANNING",
    "max_collaborators": 2,
    "visibility": "PRIVATE",
}


@pytest.fixture
def request_data():
    return {"message": "Test message", "role": "MEMBER"}


@pytest.fixture
def requests_repo(db_session: AsyncSession):
    return RequestsRepository(db_session)


@pytest.fixture
async def private_project_created(authenticated_client, db_session):
    await authenticated_client.post("/projects/api/v1/", json=PRIVATE_PROJECT_DATA)
    return await ProjectRepository(db_session).get_project_by_name(PRIVATE_PROJECT_DATA["name"])


@pytest.fixture
async def request_created(second_client, project_created, request_data, requests_repo):
    await second_client.post(
        f"/projects/api/v1/{project_created.id}/requests",
        json=request_data,
    )
    requests = await requests_repo.get_requests_by_project_id(project_created.id)
    return requests[0]
