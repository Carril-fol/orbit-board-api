from datetime import datetime, timezone

from collaborators.models.collaborators_model import Collaborators
from tasks.models.task_user_model import TaskUserStatus

URL_TASK_PREFIX = "/tasks/api/v1"
URL_PROJECT_PREFIX = "/projects/api/v1"

TASK_DATA = {"title": "Task", "status": "TO DO", "priority": "LOW"}


async def test_reassign_after_leaving_project(
    authenticated_client, second_client, member, project_created, make_task, task_user_repo, collaborators_repo
):
    task = await make_task()
    await authenticated_client.post(f"{URL_TASK_PREFIX}/{task.id}/users", json={"user_id": member.id})

    response = await second_client.delete(f"{URL_PROJECT_PREFIX}/{project_created.id}/collaborators/me")
    assert response.status_code == 200
    await collaborators_repo.create(
        Collaborators(role="MEMBER", id_user=member.id, id_project=project_created.id)
    )

    response = await authenticated_client.post(f"{URL_TASK_PREFIX}/{task.id}/users", json={"user_id": member.id})
    assert response.status_code == 200

    task_user = await task_user_repo.get_task_user_by_task_id_and_user_id(task.id, member.id)
    assert task_user.status == TaskUserStatus.ASSIGNED


async def test_filter_by_user_skips_unassigned(authenticated_client, member, project_created, make_task):
    task = await make_task()
    await authenticated_client.post(f"{URL_TASK_PREFIX}/{task.id}/users", json={"user_id": member.id})
    await authenticated_client.delete(f"{URL_TASK_PREFIX}/{task.id}/users/{member.id}")

    response = await authenticated_client.get(
        f"{URL_PROJECT_PREFIX}/{project_created.id}/tasks", params={"user_id": member.id}
    )
    assert response.status_code == 200
    assert response.json()["tasks"] == []


async def test_create_subtask_of_subtask(authenticated_client, project_created, make_task):
    parent = await make_task()
    subtask = await make_task(parent_id=parent.id)

    response = await authenticated_client.post(
        f"{URL_PROJECT_PREFIX}/{project_created.id}/tasks", json={**TASK_DATA, "parent_id": subtask.id}
    )
    assert response.status_code == 400


async def test_create_subtask_of_deleted_task(authenticated_client, project_created, make_task):
    parent = await make_task(deleted_at=datetime.now(timezone.utc))

    response = await authenticated_client.post(
        f"{URL_PROJECT_PREFIX}/{project_created.id}/tasks", json={**TASK_DATA, "parent_id": parent.id}
    )
    assert response.status_code == 404


async def test_update_task_parent_to_itself(authenticated_client, make_task):
    task = await make_task()

    response = await authenticated_client.put(f"{URL_TASK_PREFIX}/{task.id}", json={"parent_id": task.id})
    assert response.status_code == 400


async def test_update_task_with_subtasks_into_subtask(authenticated_client, make_task):
    task = await make_task()
    await make_task(parent_id=task.id)
    new_parent = await make_task()

    response = await authenticated_client.put(f"{URL_TASK_PREFIX}/{task.id}", json={"parent_id": new_parent.id})
    assert response.status_code == 400


async def test_update_task_parent(authenticated_client, make_task, task_repo):
    task = await make_task()
    new_parent = await make_task()

    response = await authenticated_client.put(f"{URL_TASK_PREFIX}/{task.id}", json={"parent_id": new_parent.id})
    assert response.status_code == 200
    assert (await task_repo.get_by_id(task.id)).parent_id == new_parent.id


async def test_create_task_on_canceled_project(authenticated_client, project_created):
    await authenticated_client.delete(f"{URL_PROJECT_PREFIX}/{project_created.id}")

    response = await authenticated_client.post(f"{URL_PROJECT_PREFIX}/{project_created.id}/tasks", json=TASK_DATA)
    assert response.status_code == 409


async def test_assign_user_to_deleted_task(authenticated_client, member, make_task):
    task = await make_task(deleted_at=datetime.now(timezone.utc))

    response = await authenticated_client.post(f"{URL_TASK_PREFIX}/{task.id}/users", json={"user_id": member.id})
    assert response.status_code == 404


async def test_get_comments_of_deleted_task(authenticated_client, make_task):
    task = await make_task(deleted_at=datetime.now(timezone.utc))

    response = await authenticated_client.get(f"{URL_TASK_PREFIX}/{task.id}/comments")
    assert response.status_code == 403


async def test_assignee_updates_task_status(authenticated_client, second_client, member, make_task, task_repo):
    task = await make_task()
    await authenticated_client.post(f"{URL_TASK_PREFIX}/{task.id}/users", json={"user_id": member.id})

    response = await second_client.put(f"{URL_TASK_PREFIX}/{task.id}", json={"status": "IN PROGRESS"})
    assert response.status_code == 200
    assert (await task_repo.get_by_id(task.id)).status == "IN PROGRESS"


async def test_assignee_cannot_update_other_fields(authenticated_client, second_client, member, make_task):
    task = await make_task()
    await authenticated_client.post(f"{URL_TASK_PREFIX}/{task.id}/users", json={"user_id": member.id})

    response = await second_client.put(f"{URL_TASK_PREFIX}/{task.id}", json={"status": "DONE", "title": "Renamed"})
    assert response.status_code == 403


async def test_unassigned_member_cannot_update_status(second_client, member, make_task):
    task = await make_task()

    response = await second_client.put(f"{URL_TASK_PREFIX}/{task.id}", json={"status": "DONE"})
    assert response.status_code == 403


async def test_get_tasks_paginated(authenticated_client, project_created, make_task):
    for _ in range(3):
        await make_task()

    response = await authenticated_client.get(
        f"{URL_PROJECT_PREFIX}/{project_created.id}/tasks", params={"limit": 2, "offset": 0}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["tasks"]) == 2
    assert body["total"] == 3
    assert body["limit"] == 2
