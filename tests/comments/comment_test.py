URL_COMMENT_PREFIX = "/comments/api/v1"
URL_TASK_PREFIX = "/tasks/api/v1"

UNKNOWN_COMMENT_ID = 2_000_000_000


async def test_create_comment(authenticated_client, task_created, comment_data, comments_repo):
    response = await authenticated_client.post(
        f"{URL_TASK_PREFIX}/{task_created.id}/comments",
        json=comment_data,
    )
    assert response.status_code == 201

    comments = await comments_repo.get_comments_by_task_id(task_created.id)
    assert len(comments) == 1
    assert comments[0].content == comment_data["content"]


async def test_create_comment_as_non_member(second_client, task_created, comment_data):
    response = await second_client.post(
        f"{URL_TASK_PREFIX}/{task_created.id}/comments",
        json=comment_data,
    )
    assert response.status_code == 403


async def test_get_comment(authenticated_client, comment_created):
    response = await authenticated_client.get(f"{URL_COMMENT_PREFIX}/{comment_created.id}")
    assert response.status_code == 200
    assert response.json()["id"] == comment_created.id
    assert response.json()["content"] == comment_created.content


async def test_get_unknown_comment(authenticated_client):
    response = await authenticated_client.get(f"{URL_COMMENT_PREFIX}/{UNKNOWN_COMMENT_ID}")
    assert response.status_code == 404


async def test_get_comments_from_task(authenticated_client, task_created, comment_created):
    response = await authenticated_client.get(f"{URL_TASK_PREFIX}/{task_created.id}/comments")
    assert response.status_code == 200

    body = response.json()
    assert body["total"] == 1
    assert body["comments"][0]["id"] == comment_created.id


async def test_get_comments_from_task_as_non_member(second_client, task_created):
    response = await second_client.get(f"{URL_TASK_PREFIX}/{task_created.id}/comments")
    assert response.status_code == 403


async def test_update_comment(authenticated_client, comment_created, comments_repo):
    response = await authenticated_client.put(
        f"{URL_COMMENT_PREFIX}/{comment_created.id}",
        json={"content": "Updated comment"},
    )
    assert response.status_code == 200

    comment = await comments_repo.get_by_id(comment_created.id)
    assert comment.content == "Updated comment"


async def test_update_comment_of_another_user(second_client, second_collaborator, comment_created):
    response = await second_client.put(
        f"{URL_COMMENT_PREFIX}/{comment_created.id}",
        json={"content": "Updated comment"},
    )
    assert response.status_code == 403


async def test_delete_comment(authenticated_client, comment_created, comments_repo):
    response = await authenticated_client.delete(f"{URL_COMMENT_PREFIX}/{comment_created.id}")
    assert response.status_code == 200
    assert await comments_repo.get_by_id(comment_created.id) is None


async def test_delete_comment_of_another_user(second_client, second_collaborator, comment_created, comments_repo):
    response = await second_client.delete(f"{URL_COMMENT_PREFIX}/{comment_created.id}")
    assert response.status_code == 403
    assert await comments_repo.get_by_id(comment_created.id) is not None
