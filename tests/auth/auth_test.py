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

async def test_register_user_with_existing_email(client: AsyncClient):
    await client.post(f"{URL_PREFIX}/register", json=DATA)

    response = await client.post(f"{URL_PREFIX}/register", json=DATA)
    assert response.status_code == 409
    
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

async def test_login_with_wrong_password(client: AsyncClient):
    await client.post(f"{URL_PREFIX}/register", json=DATA)

    response = await client.post(
        f"{URL_PREFIX}/login",
        json={
            "email": DATA["email"],
            "password": "wrongpassworD123-"
        }
    )
    assert response.status_code == 401

async def test_login_with_unknown_email(client: AsyncClient):
    response = await client.post(
        f"{URL_PREFIX}/login",
        json={
            "email": "unknown.user@example.com",
            "password": DATA["password"]
        }
    )
    assert response.status_code == 401
    
async def test_logout(authenticated_client):
    response = await authenticated_client.post(f"{URL_PREFIX}/logout")
    assert response.status_code == 200
    
async def test_refresh(authenticated_client):
    old_access = authenticated_client.cookies["refresh_token"]
    response = await authenticated_client.post(f"{URL_PREFIX}/refresh")
    
    assert response.status_code == 200
    assert authenticated_client.cookies["refresh_token"] != old_access

def use_only_cookie(client, name: str, value: str):
    client.cookies.clear()
    client.cookies.set(name, value)

async def refresh_with(client, refresh_token: str):
    use_only_cookie(client, "refresh_token", refresh_token)
    return await client.post(f"{URL_PREFIX}/refresh")

async def get_me_with(client, access_token: str):
    use_only_cookie(client, "access_token", access_token)
    return await client.get("/users/api/v1/me")

async def test_refresh_token_is_single_use(authenticated_client):
    old_refresh = authenticated_client.cookies["refresh_token"]
    await authenticated_client.post(f"{URL_PREFIX}/refresh")
    new_refresh = authenticated_client.cookies["refresh_token"]

    response = await refresh_with(authenticated_client, old_refresh)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

    response = await refresh_with(authenticated_client, new_refresh)
    assert response.status_code == 200

async def test_logout_revokes_refresh_token(authenticated_client):
    old_refresh = authenticated_client.cookies["refresh_token"]
    await authenticated_client.post(f"{URL_PREFIX}/logout")

    response = await refresh_with(authenticated_client, old_refresh)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

async def test_logout_without_session(client):
    response = await client.post(f"{URL_PREFIX}/logout")
    assert response.status_code == 200

async def test_logout_revokes_access_token(authenticated_client):
    access = authenticated_client.cookies["access_token"]
    refresh = authenticated_client.cookies["refresh_token"]
    assert (await get_me_with(authenticated_client, access)).status_code == 200

    authenticated_client.cookies.set("refresh_token", refresh)
    await authenticated_client.post(f"{URL_PREFIX}/logout")

    response = await get_me_with(authenticated_client, access)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token revoked"
