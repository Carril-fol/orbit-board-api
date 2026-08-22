import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from project_invitations.repositories.project_invitation_repository import ProjectInvitationRepository

FULL_PROJECT_DATA = {
    "name": "Full project tests",
    "description": "Project description",
    "status": "PLANNING",
    "max_collaborators": 1,
    "visibility": "PUBLIC",
}


@pytest.fixture
def invitations_repo(db_session: AsyncSession):
    return ProjectInvitationRepository(db_session)


@pytest.fixture
def invitation_data(project_created, second_user):
    return {
        "id_project": project_created.id,
        "id_invitee": second_user.id,
        "role": "MEMBER",
    }


@pytest.fixture
async def invitation_created(
    authenticated_client, 
    invitation_data, 
    invitations_repo, 
    project_created, 
    second_user
):
    await authenticated_client.post("/invitations/api/v1/", json=invitation_data)
    return await invitations_repo.get_invite_by_project_id_and_invitee_id(project_created.id, second_user.id)
