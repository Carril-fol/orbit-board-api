from core.security.password_manager import PasswordManager
from users.interfaces import IUserService

from ..exceptions import (
    InvalidCredentialsException,
    AuthUserAlreadyExistWithThatEmail
)
from ..schemas.auth_schema import (
    LoginInputSchema,
    RegisterInputSchema
)
from ..interfaces import IAuthService


class AuthService(IAuthService):
    
    def __init__(
        self, 
        user_service: IUserService, 
        password_manager: PasswordManager
    ):
        self.user_service = user_service
        self.password_manager = password_manager

    async def register_user(self, data: RegisterInputSchema):
        if await self.user_service.get_user_by_email(data.email):
            raise AuthUserAlreadyExistWithThatEmail()

        hashed_password = await self.password_manager.hash(data.password)
        return await self.user_service.create_user(data, hashed_password)

    async def authenticate(self, data: LoginInputSchema):
        user = await self.user_service.get_user_by_email(data.email)
        if not user:
            raise InvalidCredentialsException()

        if not await self.password_manager.verify(data.password, user.password):
            raise InvalidCredentialsException()

        return user.id
