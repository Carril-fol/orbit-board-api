
URL_PREFIX = "/projects/api/v1"

DATA = {
    "name": "Project tests",
    "description": "Project description",
    "status": "PLANNING",
    "max_collaborators": 2,
    "visibility": "PUBLIC"
}

async def test_create_project(authenticated_client):
    response = await authenticated_client.post(f"{URL_PREFIX}/", json=DATA)
    assert response.status_code == 201
        
async def test_get_project(project_created, project_repo):
    project = await project_repo.get_project_by_name(DATA["name"])
    assert project.name == DATA["name"]
    
async def test_update_project(project_created, authenticated_client, project_repo):
    project = await project_repo.get_project_by_name(DATA["name"])
    
    response_update = await authenticated_client.patch(f"{URL_PREFIX}/{project.id}", json={"name": "Project updated"})
    assert response_update.status_code == 200
    
async def test_delete_project(project_created, authenticated_client, project_repo):    
    project = await project_repo.get_project_by_name(DATA["name"])

    response_delete = await authenticated_client.delete(f"{URL_PREFIX}/{project.id}")
    assert response_delete.status_code == 200
    
async def test_get_my_projects(project_created, authenticated_client):
    response_get_my_projects = await authenticated_client.get(f"{URL_PREFIX}/me")
    assert response_get_my_projects.status_code == 200
    
async def test_get_all_projects(project_created, authenticated_client):
    response_get_my_projects = await authenticated_client.get(f"{URL_PREFIX}/")
    assert response_get_my_projects.status_code == 200

async def test_project_detail_has_timestamps(project_created, authenticated_client):
    response = await authenticated_client.get(f"{URL_PREFIX}/{project_created.id}")
    assert response.status_code == 200
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is not None
