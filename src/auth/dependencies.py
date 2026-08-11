from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.password_manager import PasswordManager
from shared.database import get_async_db

from users.repositories.user_repository import UserRepository

from .services.auth_services import AuthService


def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    return UserRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    password_manager: PasswordManager = Depends()
):
    return AuthService(user_repo, password_manager)