from main import app
from shared.database import get_async_db


class UnreachableDatabase:
    async def execute(self, *args, **kwargs):
        raise ConnectionRefusedError()


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_health_with_database_down(client):
    previous = app.dependency_overrides[get_async_db]
    app.dependency_overrides[get_async_db] = lambda: UnreachableDatabase()
    try:
        response = await client.get("/health")
    finally:
        app.dependency_overrides[get_async_db] = previous

    assert response.status_code == 503
    assert response.json()["detail"] == "Database unavailable"
