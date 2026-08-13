from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from .interfaces import IUserService
from .repositories.user_repository import UserRepository
from .services.user_service import UserService


def get_user_repository(
    db: AsyncSession = Depends(get_async_db),
) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> IUserService:
    return UserService(user_repo)