from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.base_repository import BaseRepository
from ..models.user import User

class UserRepository(BaseRepository[User]):

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).filter(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()