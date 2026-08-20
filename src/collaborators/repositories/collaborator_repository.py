from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from users.models.user import User
from shared.database.base_repository import BaseRepository

from ..models.collaborators_model import Collaborators


class CollaboratorRepository(BaseRepository[Collaborators]):

    def __init__(self, db: AsyncSession):
        super().__init__(Collaborators, db)

    async def get_collaborators_from_project(self, id_project: int):
        stmt = (
            select(Collaborators)
            .join(Collaborators.user)
            .where(
                User.id == Collaborators.id_user,
                Collaborators.id_project == id_project
            )
            .options(selectinload(Collaborators.user))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_collaborators_from_project(self, id_project: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Collaborators)
            .where(Collaborators.id_project == id_project)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_collaborator_by_user_id(self, user_id: int):
        stmt = select(Collaborators).where(Collaborators.id_user == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_collaborator_by_user_id_and_project_id(self, user_id: int, id_project: int):
        stmt = select(Collaborators).where(
            Collaborators.id_user == user_id,
            Collaborators.id_project == id_project
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
