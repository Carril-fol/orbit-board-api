from datetime import datetime, timedelta, timezone

import jwt
from httpx import AsyncClient

from auth.repositories.revoked_token_repository import RevokedTokenRepository
from core.security.jwt_manager import JwtManager
from shared.extensions import limiter

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

async def test_register_user_with_existing_username(client: AsyncClient):
    await client.post(f"{URL_PREFIX}/register", json=DATA)

    response = await client.post(f"{URL_PREFIX}/register", json={**DATA, "email": "other@example.com"})
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

def expired_token(token_type: str) -> str:
    payload = {
        "sub": "1",
        "jti": "expired-token",
        "type": token_type,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    return jwt.encode(payload, JwtManager.SECRET_KEY, algorithm=JwtManager.ALGORITHM)

async def test_protected_route_without_token(client):
    response = await client.get("/users/api/v1/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Access token not found"

async def test_refresh_without_token(client):
    response = await client.post(f"{URL_PREFIX}/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token not found"

async def test_expired_access_token(client):
    response = await get_me_with(client, expired_token("access_token"))
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"

async def test_malformed_access_token(client):
    response = await get_me_with(client, "not-a-jwt")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

async def test_refresh_token_used_as_access_token(authenticated_client):
    refresh = authenticated_client.cookies["refresh_token"]
    response = await get_me_with(authenticated_client, refresh)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access_token token"

async def test_logout_with_expired_token(client):
    use_only_cookie(client, "access_token", expired_token("access_token"))
    response = await client.post(f"{URL_PREFIX}/logout")
    assert response.status_code == 200

async def test_login_rate_limit(client):
    limiter.reset()
    limiter.enabled = True
    try:
        credentials = {"email": DATA["email"], "password": DATA["password"]}
        statuses = [
            (await client.post(f"{URL_PREFIX}/login", json=credentials)).status_code
            for _ in range(6)
        ]
    finally:
        limiter.enabled = False
        limiter.reset()

    assert statuses[:5] == [401] * 5
    assert statuses[5] == 429

async def test_logout_purges_expired_revoked_tokens(authenticated_client, db_session):
    repo = RevokedTokenRepository(db_session)
    await repo.revoke("expired-jti", datetime.now(timezone.utc) - timedelta(minutes=1))
    access_jti = JwtManager.decode_token(authenticated_client.cookies["access_token"])["jti"]

    response = await authenticated_client.post(f"{URL_PREFIX}/logout")
    assert response.status_code == 200

    assert not await repo.is_revoked("expired-jti")
    assert await repo.is_revoked(access_jti)
