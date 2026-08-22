URL_COLLABORATOR_PREFIX = "/collaborators/api/v1"
URL_PROJECT_PREFIX = "/projects/api/v1"

UNKNOWN_COLLABORATOR_ID = 2_000_000_000


async def test_get_collaborators(authenticated_client, project_created, collaborator_created, second_user):
    response = await authenticated_client.get(f"{URL_PROJECT_PREFIX}/{project_created.id}/collaborators")
    assert response.status_code == 200

    collaborators = response.json()["collaborators"]
    assert len(collaborators) == 2
    assert second_user.id in [collaborator["user"]["id"] for collaborator in collaborators]


async def test_get_collaborators_as_non_member(second_client, project_created):
    response = await second_client.get(f"{URL_PROJECT_PREFIX}/{project_created.id}/collaborators")
    assert response.status_code == 403


async def test_change_role_collaborator(authenticated_client, collaborator_created, collaborators_repo):
    response = await authenticated_client.patch(
        f"{URL_COLLABORATOR_PREFIX}/{collaborator_created.id}",
        json={"role": "admin"},
    )
    assert response.status_code == 200

    collaborator = await collaborators_repo.get_by_id(collaborator_created.id)
    assert collaborator.role == "ADMIN"


async def test_change_role_collaborator_as_non_owner(second_client, collaborator_created):
    response = await second_client.patch(
        f"{URL_COLLABORATOR_PREFIX}/{collaborator_created.id}",
        json={"role": "ADMIN"},
    )
    assert response.status_code == 403


async def test_change_role_unknown_collaborator(authenticated_client):
    response = await authenticated_client.patch(
        f"{URL_COLLABORATOR_PREFIX}/{UNKNOWN_COLLABORATOR_ID}",
        json={"role": "ADMIN"},
    )
    assert response.status_code == 404


async def test_remove_collaborator(authenticated_client, collaborator_created, collaborators_repo):
    response = await authenticated_client.delete(f"{URL_COLLABORATOR_PREFIX}/{collaborator_created.id}")
    assert response.status_code == 200
    assert await collaborators_repo.get_by_id(collaborator_created.id) is None


async def test_remove_collaborator_as_non_owner(second_client, collaborator_created, collaborators_repo):
    response = await second_client.delete(f"{URL_COLLABORATOR_PREFIX}/{collaborator_created.id}")
    assert response.status_code == 403
    assert await collaborators_repo.get_by_id(collaborator_created.id) is not None
