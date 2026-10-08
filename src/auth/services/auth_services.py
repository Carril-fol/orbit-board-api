from datetime import datetime, timezone

from fastapi import HTTPException

from core.security.jwt_manager import JwtManager
from core.security.password_manager import PasswordManager
from users.interfaces import IUserService

from ..exceptions import (
    InvalidCredentialsException,
    InvalidTokenExceptions,
    AuthUserAlreadyExistWithThatEmail
)
from ..repositories.revoked_token_repository import RevokedTokenRepository
from ..schemas.auth_schema import (
    LoginInputSchema,
    RegisterInputSchema
)
from ..interfaces import IAuthService


class AuthService(IAuthService):
    
    def __init__(
        self, 
        user_service: IUserService, 
        password_manager: PasswordManager,
        revoked_token_repo: RevokedTokenRepository,
    ):
        self.user_service = user_service
        self.password_manager = password_manager
        self.revoked_token_repo = revoked_token_repo

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

    async def _revoke(self, payload: dict) -> bool:
        expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
        return await self.revoked_token_repo.revoke(payload["jti"], expires_at)

    async def rotate_refresh_token(self, payload: dict) -> None:
        # A refresh token is single use: a revoked one means logout or replay.
        if not await self._revoke(payload):
            raise InvalidTokenExceptions()

    async def logout(self, access_token: str | None, refresh_token: str | None) -> None:
        for token, token_type in ((access_token, "access_token"), (refresh_token, "refresh_token")):
            if not token:
                continue
            try:
                payload = JwtManager.validate_token(token, token_type)
            except HTTPException:
                continue  # expired or forged: it can't be used anyway
            await self._revoke(payload)
