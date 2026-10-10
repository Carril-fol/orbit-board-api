from tasks.models.task_user_model import TaskUserStatus
from tasks.repositories.task_repository import TaskRepository
from tasks.repositories.task_user_repository import TaskUserRepository

URL_COLLABORATOR_PREFIX = "/collaborators/api/v1"
URL_PROJECT_PREFIX = "/projects/api/v1"

UNKNOWN_COLLABORATOR_ID = 2_000_000_000
UNKNOWN_PROJECT_ID = 2_000_000_000


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


async def test_leave_project(authenticated_client, second_client, project_created, collaborator_created, collaborators_repo):
    response = await second_client.delete(f"{URL_PROJECT_PREFIX}/{project_created.id}/collaborators/me")
    assert response.status_code == 200
    assert await collaborators_repo.get_by_id(collaborator_created.id) is None

    notifications = (await authenticated_client.get("/notifications/api/v1/")).json()["notifications"]
    assert notifications[0]["type"] == "collaborator_left"


async def test_leave_project_unassigns_tasks(
    authenticated_client, second_client, second_user, project_created, collaborator_created, db_session
):
    await authenticated_client.post(
        f"{URL_PROJECT_PREFIX}/{project_created.id}/tasks",
        json={"title": "Task tests", "description": "Task description", "status": "TO DO", "priority": "MEDIUM"},
    )
    task = (await TaskRepository(db_session).get_tasks_by_project(project_created.id))[0][0]
    await authenticated_client.post(f"/tasks/api/v1/{task.id}/users", json={"user_id": second_user.id})

    await second_client.delete(f"{URL_PROJECT_PREFIX}/{project_created.id}/collaborators/me")

    task_user = await TaskUserRepository(db_session).get_task_user_by_task_id_and_user_id(task.id, second_user.id)
    assert task_user.status == TaskUserStatus.UNASSIGNED


async def test_leave_project_as_owner(authenticated_client, project_created):
    response = await authenticated_client.delete(f"{URL_PROJECT_PREFIX}/{project_created.id}/collaborators/me")
    assert response.status_code == 409


async def test_leave_project_as_non_member(second_client, project_created):
    response = await second_client.delete(f"{URL_PROJECT_PREFIX}/{project_created.id}/collaborators/me")
    assert response.status_code == 403


async def test_leave_unknown_project(authenticated_client):
    response = await authenticated_client.delete(f"{URL_PROJECT_PREFIX}/{UNKNOWN_PROJECT_ID}/collaborators/me")
    assert response.status_code == 404


async def test_remove_project_owner(authenticated_client, project_created, collaborators_repo):
    owner = await collaborators_repo.get_collaborator_by_user_id_and_project_id(project_created.owner_id, project_created.id)

    response = await authenticated_client.delete(f"{URL_COLLABORATOR_PREFIX}/{owner.id}")
    assert response.status_code == 409
