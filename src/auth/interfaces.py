from abc import ABC, abstractmethod
from .schemas.auth_schema import LoginInputSchema, RegisterInputSchema

class IAuthService(ABC):
    
    @abstractmethod
    async def register_user(self, data: RegisterInputSchema):
        pass

    @abstractmethod
    async def authenticate(self, data: LoginInputSchema):
        pass

    @abstractmethod
    async def rotate_refresh_token(self, payload: dict) -> None:
        pass

    @abstractmethod
    async def logout(self, access_token: str | None, refresh_token: str | None) -> None:
        pass
