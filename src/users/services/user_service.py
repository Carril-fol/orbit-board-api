from ..models.user import User
from ..exceptions import UserNotFound
from ..interfaces import IUserService
from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import  UserCreateSchema


class UserService(IUserService):

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def create_user(self, data: UserCreateSchema, hashed_password: str) -> User:        
        user_create = UserCreateSchema(
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            email=data.email,
            password=hashed_password,
        )
        user_entity = User(**user_create.model_dump())
        return await self.user_repo.create(user_entity)
    
    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        return user

    async def get_user_by_email(self, email: str) -> User:
        user = await self.user_repo.get_user_by_email(email)
        return user