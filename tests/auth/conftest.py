import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from users.services.user_service import UserService
from users.repositories.user_repository import UserRepository

@pytest.fixture
def user_service(db_session: AsyncSession):
    return UserService(UserRepository(db_session))