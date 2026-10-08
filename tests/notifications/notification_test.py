import pytest

from collaborators.models.collaborators_model import Collaborators
from requests.repositories.requests_repository import RequestsRepository
from tasks.repositories.task_repository import TaskRepository

URL_PREFIX = "/notifications/api/v1"


async def notification_types(client) -> list[str]:
    response = await client.get(f"{URL_PREFIX}/")
    return [notification["type"] for notification in response.json()["notifications"]]


@pytest.fixture
async def invitation_sent(authenticated_client, project_created, second_user):
    response = await authenticated_client.post(
        "/invitations/api/v1/",
        json={"id_project": project_created.id, "invitee_email": second_user.email, "role": "MEMBER"},
    )
    return response.json()["token"]


@pytest.fixture
async def request_sent(second_client, project_created, db_session):
    await second_client.post(
        f"/projects/api/v1/{project_created.id}/requests",
        json={"message": "Test message", "role": "MEMBER"},
    )
    requests = await RequestsRepository(db_session).get_requests_by_project_id(project_created.id)
    return requests[0]


@pytest.fixture
async def collaborator_created(second_user, project_created, collaborators_repo):
    return await collaborators_repo.create(
        Collaborators(role="MEMBER", id_user=second_user.id, id_project=project_created.id)
    )


@pytest.fixture
async def task_created(authenticated_client, project_created, db_session):
    await authenticated_client.post(
        f"/projects/api/v1/{project_created.id}/tasks",
        json={"title": "Task tests", "description": "Task description", "status": "TO DO", "priority": "MEDIUM"},
    )
    tasks = await TaskRepository(db_session).get_tasks_by_project(project_created.id)
    return tasks[0]


async def test_invitation_notifies_invitee(second_client, invitation_sent, project_created):
    response = await second_client.get(f"{URL_PREFIX}/")
    assert response.status_code == 200

    body = response.json()
    assert body["total"] == 1
    assert body["unread"] == 1
    assert body["notifications"][0]["type"] == "invitation_received"
    assert body["notifications"][0]["data"]["project_id"] == project_created.id
    assert body["notifications"][0]["read_at"] is None


async def test_inviter_gets_no_notification(authenticated_client, invitation_sent):
    response = await authenticated_client.get(f"{URL_PREFIX}/")
    assert response.json()["total"] == 0


async def test_mark_notification_as_read(second_client, invitation_sent):
    notification_id = (await second_client.get(f"{URL_PREFIX}/")).json()["notifications"][0]["id"]

    response = await second_client.patch(f"{URL_PREFIX}/{notification_id}/read")
    assert response.status_code == 200

    body = (await second_client.get(f"{URL_PREFIX}/")).json()
    assert body["unread"] == 0
    assert body["notifications"][0]["read_at"] is not None


async def test_mark_notification_of_another_user(authenticated_client, second_client, invitation_sent):
    notification_id = (await second_client.get(f"{URL_PREFIX}/")).json()["notifications"][0]["id"]

    response = await authenticated_client.patch(f"{URL_PREFIX}/{notification_id}/read")
    assert response.status_code == 404


async def test_mark_all_notifications_as_read(second_client, invitation_sent):
    response = await second_client.patch(f"{URL_PREFIX}/read-all")
    assert response.status_code == 200

    assert (await second_client.get(f"{URL_PREFIX}/")).json()["unread"] == 0


@pytest.mark.parametrize("action, expected_type", [
    ("accept", "invitation_accepted"),
    ("reject", "invitation_rejected"),
])
async def test_invitation_response_notifies_inviter(authenticated_client, second_client, invitation_sent, action, expected_type):
    await second_client.post(f"/invitations/api/v1/{invitation_sent}/{action}")

    assert await notification_types(authenticated_client) == [expected_type]


async def test_request_notifies_project_owner(authenticated_client, request_sent):
    assert await notification_types(authenticated_client) == ["request_received"]


@pytest.mark.parametrize("action, expected_type", [
    ("approve", "request_approved"),
    ("decline", "request_declined"),
])
async def test_request_response_notifies_requester(authenticated_client, second_client, request_sent, action, expected_type):
    await authenticated_client.post(f"/requests/api/v1/{request_sent.id}/{action}")

    assert await notification_types(second_client) == [expected_type]


async def test_task_assignment_notifies_assignee(authenticated_client, second_client, second_user, collaborator_created, task_created):
    await authenticated_client.post(f"/tasks/api/v1/{task_created.id}/users", json={"user_id": second_user.id})
    await authenticated_client.delete(f"/tasks/api/v1/{task_created.id}/users/{second_user.id}")

    assert await notification_types(second_client) == ["task_unassigned", "task_assigned"]


async def test_role_change_notifies_collaborator(authenticated_client, second_client, collaborator_created):
    await authenticated_client.patch(f"/collaborators/api/v1/{collaborator_created.id}", json={"role": "admin"})

    assert await notification_types(second_client) == ["role_changed"]


async def test_removal_notifies_collaborator(authenticated_client, second_client, collaborator_created):
    await authenticated_client.delete(f"/collaborators/api/v1/{collaborator_created.id}")

    assert await notification_types(second_client) == ["removed_from_project"]


async def test_own_actions_are_not_notified(authenticated_client, task_created):
    me = (await authenticated_client.get("/users/api/v1/me")).json()
    response = await authenticated_client.post(f"/tasks/api/v1/{task_created.id}/users", json={"user_id": me["id"]})
    assert response.status_code == 200

    assert await notification_types(authenticated_client) == []


async def test_failed_notification_keeps_transaction_usable(db_session, second_user):
    from sqlalchemy import select
    from notifications.repositories.notification_repository import NotificationRepository
    from notifications.services.notification_service import NotificationService

    service = NotificationService(NotificationRepository(db_session))

    # Unknown recipient violates the FK: must be swallowed, not abort the transaction.
    await service.notify(user_id=2_000_000_000, actor_id=second_user.id, type="test", data={})

    assert (await db_session.execute(select(1))).scalar_one() == 1
