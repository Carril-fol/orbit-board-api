import pytest

from collaborators.models.collaborators_model import Collaborators


@pytest.fixture
async def collaborator_created(second_user, project_created, collaborators_repo):
    collaborator = Collaborators(
        role="MEMBER",
        id_user=second_user.id,
        id_project=project_created.id,
    )
    return await collaborators_repo.create(collaborator)
