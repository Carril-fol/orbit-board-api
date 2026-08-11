from core.security.password_manager import PasswordManager
from users.models.user import User
from users.repositories.user_repository import UserRepository

from ..auth_exception import (
    InvalidCredentialsException,
    AuthUserAlreadyExistWithThatEmail
)
from ..schemas.auth_schema import (
    LoginInputSchema,
    RegisterInputSchema,
    UserCreateSchema,
)


class AuthService:
    def __init__(self, user_repo: UserRepository, password_manager: PasswordManager):
        self.user_repo = user_repo
        self.password_manager = password_manager

    async def _get_user_by_email_or_raise(self, email: str):
        user = await self.user_repo.get_user_by_email(email)
        return user

    async def register_user(self, data: RegisterInputSchema):
        if await self._get_user_by_email_or_raise(data.email):
            raise AuthUserAlreadyExistWithThatEmail()

        hashed_password = self.password_manager.hash(data.password)
        user_create = UserCreateSchema(
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            email=data.email,
            password=hashed_password,
        )
        user_entity = User(**user_create.model_dump())
        return await self.user_repo.create(user_entity)

    async def authenticate(self, data: LoginInputSchema):
        user = await self._get_user_by_email_or_raise(data.email)
        if not user:
            raise InvalidCredentialsException("Invalid credentials")
        
        if not self.password_manager.verify(data.password, user.password):
            raise InvalidCredentialsException("Invalid credentials")

        return user.id
