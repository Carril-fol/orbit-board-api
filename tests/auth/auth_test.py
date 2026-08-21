from httpx import AsyncClient

URL_PREFIX = "/auth/api/v1"

DATA = {
    "first_name": "Test",
    "last_name": "Test",
    "username": "Test Username",
    "email": "test.test@example.com",
    "password": "testpassworD123-",
    "confirm_password": "testpassworD123-",
}

async def test_register_user(client: AsyncClient, user_service):
    response = await client.post(f"{URL_PREFIX}/register", json=DATA)
    assert response.status_code == 201
    
    user = await user_service.get_user_by_email(DATA["email"])
    assert user is not None
    assert user.username == DATA["username"]
    
async def test_login(client: AsyncClient):
    await client.post(f"{URL_PREFIX}/register", json=DATA)

    response = await client.post(
        f"{URL_PREFIX}/login", 
        json={
            "email": "test.test@example.com", 
            "password": "testpassworD123-"
        }
    )
    assert response.status_code == 200
    
async def test_logout(authenticated_client):
    response = await authenticated_client.post(f"{URL_PREFIX}/logout")
    assert response.status_code == 200
    
async def test_refresh(authenticated_client):
    old_access = authenticated_client.cookies["refresh_token"]
    response = await authenticated_client.post(f"{URL_PREFIX}/refresh")
    
    assert response.status_code == 200
    assert authenticated_client.cookies["refresh_token"] != old_access