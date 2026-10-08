from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.password_manager import PasswordManager
from shared.database import get_async_db

from users.dependencies import get_user_service
from users.interfaces import IUserService

from .interfaces import IAuthService
from .repositories.revoked_token_repository import RevokedTokenRepository
from .services.auth_services import AuthService


def get_revoked_token_repository(
    db: AsyncSession = Depends(get_async_db, scope="function"),
) -> RevokedTokenRepository:
    return RevokedTokenRepository(db)


def get_auth_service(
    user_service: IUserService = Depends(get_user_service),
    password_manager: PasswordManager = Depends(),
    revoked_token_repo: RevokedTokenRepository = Depends(get_revoked_token_repository),
) -> IAuthService:
    return AuthService(user_service, password_manager, revoked_token_repo)
