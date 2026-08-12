from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.base_repository import BaseRepository

from ..models.task_user_model import TaskUser


class TaskUserRepository(BaseRepository[TaskUser]):

    def __init__(self, db: AsyncSession):
        super().__init__(TaskUser, db)

    async def assign_user(self, task_id: int, user_id: int):
        stmt = select(TaskUser).where(
            TaskUser.task_id == task_id,
            TaskUser.user_id == user_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        assignment = TaskUser(task_id=task_id, user_id=user_id)
        await self.create(assignment)
        return assignment

    async def get_task_user_by_task_id_and_user_id(self, task_id: int, user_id: int):
        stmt = select(TaskUser).where(
            TaskUser.task_id == task_id,
            TaskUser.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
