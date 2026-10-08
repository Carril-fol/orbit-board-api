from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload

from users.models.user import User
from tasks.models.task_model import Task
from tasks.models.task_user_model import TaskUser, TaskUserStatus
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

    async def unassign_user_from_project_tasks(self, user_id: int, project_id: int) -> None:
        stmt = (
            update(TaskUser)
            .where(
                TaskUser.user_id == user_id,
                TaskUser.status == TaskUserStatus.ASSIGNED,
                TaskUser.task_id.in_(select(Task.id).where(Task.project_id == project_id)),
            )
            .values(status=TaskUserStatus.UNASSIGNED, updated_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
