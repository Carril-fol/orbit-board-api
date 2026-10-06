import os

os.environ["ENV"] = "testing"

import subprocess
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from collaborators.repositories.collaborator_repository import CollaboratorRepository
from main import app
from projects.repositories.project_repository import ProjectRepository
from shared.database import engine, get_async_db
from shared.extensions import limiter
from users.repositories.user_repository import UserRepository

ROOT_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT_DIR,
        check=True,
    )


@pytest.fixture(scope="session", autouse=True)
def disable_rate_limit():
    limiter.enabled = False
    yield
    limiter.enabled = True

@pytest.fixture
async def db_session():
    connection = await engine.connect()
    transaction = await connection.begin()
    session = async_sessionmaker(bind=connection, expire_on_commit=False)()
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_async_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client
        
USER_DATA = {
    "first_name": "Test",
    "last_name": "Test",
    "username": "Test Username",
    "email": "test.test@example.com",
    "password": "testpassworD123-",
    "confirm_password": "testpassworD123-",
}

async def _register_and_login(async_client: AsyncClient, user_data: dict) -> AsyncClient:
    await async_client.post("/auth/api/v1/register", json=user_data)
    await async_client.post(
        "/auth/api/v1/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    return async_client

@pytest.fixture
async def authenticated_client(client):
    return await _register_and_login(client, USER_DATA)

@pytest.fixture
async def make_client(client):
    """Factory: each call returns a new client logged in as the given user."""
    clients = []

    async def _make(user_data: dict) -> AsyncClient:
        async_client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        clients.append(async_client)
        return await _register_and_login(async_client, user_data)

    yield _make
    for async_client in clients:
        await async_client.aclose()

SECOND_USER_DATA = {
    "first_name": "Second",
    "last_name": "Test",
    "username": "Second Username",
    "email": "second.test@example.com",
    "password": "testpassworD123-",
    "confirm_password": "testpassworD123-",
}

@pytest.fixture
async def anonymous_client(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client

@pytest.fixture
async def second_client(authenticated_client, make_client):
    return await make_client(SECOND_USER_DATA)

@pytest.fixture
async def second_user(second_client, db_session):
    return await UserRepository(db_session).get_user_by_email(SECOND_USER_DATA["email"])

@pytest.fixture
def collaborators_repo(db_session):
    return CollaboratorRepository(db_session)

PROJECT_DATA = {
    "name": "Project tests",
    "description": "Project description",
    "status": "PLANNING",
    "max_collaborators": 2,
    "visibility": "PUBLIC"
}

@pytest.fixture
async def project_created(authenticated_client, db_session):
    await authenticated_client.post("/projects/api/v1/", json=PROJECT_DATA)
    return await ProjectRepository(db_session).get_project_by_name(PROJECT_DATA["name"])
