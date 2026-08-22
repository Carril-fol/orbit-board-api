from requests.schemas.requests_schemas import RequestStatus

URL_REQUEST_PREFIX = "/requests/api/v1"
URL_PROJECT_PREFIX = "/projects/api/v1"


async def test_create_request(second_client, project_created, request_data, requests_repo):
    response = await second_client.post(
        f"{URL_PROJECT_PREFIX}/{project_created.id}/requests",
        json=request_data,
    )
    assert response.status_code == 201

    requests = await requests_repo.get_requests_by_project_id(project_created.id)
    assert len(requests) == 1
    assert requests[0].status == RequestStatus.PENDING


async def test_get_all_requests(authenticated_client, project_created):
    response = await authenticated_client.get(f"{URL_PROJECT_PREFIX}/{project_created.id}/requests")
    assert response.status_code == 200


async def test_get_all_requests_as_non_owner(second_client, project_created):
    response = await second_client.get(f"{URL_PROJECT_PREFIX}/{project_created.id}/requests")
    assert response.status_code == 403


async def test_get_request(authenticated_client, request_created):
    response = await authenticated_client.get(f"{URL_REQUEST_PREFIX}/{request_created.id}")
    assert response.status_code == 200
    assert response.json()["id"] == request_created.id
    assert response.json()["status"] == RequestStatus.PENDING


async def test_get_sent_requests(second_client):
    response = await second_client.get(f"{URL_REQUEST_PREFIX}/sent")
    assert response.status_code == 200


async def test_approve_request(authenticated_client, request_created, requests_repo, collaborators_repo):
    response = await authenticated_client.post(f"{URL_REQUEST_PREFIX}/{request_created.id}/approve")
    assert response.status_code == 201

    request = await requests_repo.get_request_by_id(request_created.id)
    assert request.status == RequestStatus.APPROVED
    assert request.review_at is not None

    collaborator = await collaborators_repo.get_collaborator_by_user_id_and_project_id(
        request_created.user_id,
        request_created.project_id,
    )
    assert collaborator is not None
    assert collaborator.role == request_created.role


async def test_decline_request(authenticated_client, request_created, requests_repo, collaborators_repo):
    response = await authenticated_client.post(f"{URL_REQUEST_PREFIX}/{request_created.id}/decline")
    assert response.status_code == 200

    request = await requests_repo.get_request_by_id(request_created.id)
    assert request.status == RequestStatus.REJECTED
    assert request.review_at is not None

    collaborator = await collaborators_repo.get_collaborator_by_user_id_and_project_id(
        request_created.user_id,
        request_created.project_id,
    )
    assert collaborator is None


async def test_approve_request_as_non_owner(second_client, request_created):
    response = await second_client.post(f"{URL_REQUEST_PREFIX}/{request_created.id}/approve")
    assert response.status_code == 403