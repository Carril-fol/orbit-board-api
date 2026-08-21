PROJECTS_URL_PREFIX = "/projects/api/v1"
TAGS_URL_PREFIX = "/project-tags/api/v1"

async def test_create_project_tag(authenticated_client, project_created, tag_data):
    response = await authenticated_client.post(
        f"{PROJECTS_URL_PREFIX}/{project_created.id}/tags",
        json=tag_data,
    )
    assert response.status_code == 201

async def test_delete_project_tag(authenticated_client, project_tag_created, project_tag_repo):
    response = await authenticated_client.delete(f"{TAGS_URL_PREFIX}/{project_tag_created.id}")
    assert response.status_code == 200
    assert await project_tag_repo.get_project_tag_by_id(project_tag_created.id) is None
