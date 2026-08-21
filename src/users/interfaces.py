from abc import ABC, abstractmethod

from .models.user import User
from .schemas.user_schema import UserCreateSchema


class IUserService(ABC):
    
    @abstractmethod
    async def get_user_by_email(self, email: str):
        pass
    
    @abstractmethod
    async def create_user(self, data: UserCreateSchema):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User:
        pass