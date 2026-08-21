import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from main import app
from shared.database import engine, get_async_db
from shared.extensions import limiter

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
        
@pytest.fixture
async def authenticated_client(client):
    DATA = {
        "first_name": "Test",
        "last_name": "Test",
        "username": "Test Username",
        "email": "test.test@example.com",
        "password": "testpassworD123-",
        "confirm_password": "testpassworD123-",
    }
    
    await client.post("/auth/api/v1/register", json=DATA)

    await client.post(
        "/auth/api/v1/login",
        json={
            "email": "test.test@example.com", 
            "password": "testpassworD123-"
        }
    )
    
    return client