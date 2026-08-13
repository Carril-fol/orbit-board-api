from fastapi import Depends

from core.security.password_manager import PasswordManager

from users.dependencies import get_user_service
from users.interfaces import IUserService

from .interfaces import IAuthService
from .services.auth_services import AuthService


def get_auth_service(
    user_service: IUserService = Depends(get_user_service),
    password_manager: PasswordManager = Depends()
) -> IAuthService:
    return AuthService(user_service, password_manager)