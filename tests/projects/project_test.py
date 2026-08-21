
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
        
async def test_get_project(authenticated_client, project_repo):
    response = await authenticated_client.post(f"{URL_PREFIX}/", json=DATA)
    assert response.status_code == 201
    
    project = await project_repo.get_project_by_name(DATA["name"])
    assert project.name == DATA["name"]
    
async def test_update_project(authenticated_client, project_repo):
    response = await authenticated_client.post(f"{URL_PREFIX}/", json=DATA)
    assert response.status_code == 201
    
    project = await project_repo.get_project_by_name(DATA["name"])
    
    response_update = await authenticated_client.patch(f"{URL_PREFIX}/{project.id}", json={"name": "Project updated"})
    assert response_update.status_code == 200
    
async def test_delete_project(authenticated_client, project_repo):
    response = await authenticated_client.post(f"{URL_PREFIX}/", json=DATA)
    assert response.status_code == 201
    
    project = await project_repo.get_project_by_name(DATA["name"])

    response_delete = await authenticated_client.delete(f"{URL_PREFIX}/{project.id}")
    assert response_delete.status_code == 200
    
async def test_get_my_projects(authenticated_client):
    response_created = await authenticated_client.post(f"{URL_PREFIX}/", json=DATA)
    assert response_created.status_code == 201

    response_get_my_projects = await authenticated_client.get(f"{URL_PREFIX}/me")
    assert response_get_my_projects.status_code == 200
    
async def test_get_all_projects(authenticated_client):
    response_created = await authenticated_client.post(f"{URL_PREFIX}/", json=DATA)
    assert response_created.status_code == 201

    response_get_my_projects = await authenticated_client.get(f"{URL_PREFIX}/")
    assert response_get_my_projects.status_code == 200