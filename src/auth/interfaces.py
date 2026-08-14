from abc import ABC, abstractmethod
from .schemas.auth_schema import LoginInputSchema, RegisterInputSchema

class IAuthService(ABC):
    
    @abstractmethod
    async def register_user(self, data: RegisterInputSchema):
        pass

    @abstractmethod
    async def authenticate(self, data: LoginInputSchema):
        pass
