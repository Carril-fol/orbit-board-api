from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.base_repository import BaseRepository
from ..models.task_model import Task, TaskStatus
from ..models.task_user_model import TaskUser


class TaskRepository(BaseRepository[Task]):

    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_tasks_by_project(self, project_id: int, status: str = None, priority: str = None, user_id: int = None):
        stmt = select(self.model).where(
            self.model.project_id == project_id,
            self.model.parent_id == None,
            self.model.deleted_at == None
        )

        if status:
            stmt = stmt.where(self.model.status == status)
        if priority:
            stmt = stmt.where(self.model.priority == priority)
        if user_id:
            stmt = stmt.join(TaskUser).where(TaskUser.user_id == user_id)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_tasks_from_project_from_user(self, user_id: int, project_id: int):
        stmt = select(self.model).join(TaskUser).where(
            TaskUser.user_id == user_id,
            self.model.project_id == project_id,
            self.model.parent_id == None,
            self.model.deleted_at == None
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_tasks_with_priority(self, priority: str):
        stmt = select(self.model).where(
            self.model.priority == priority,
            self.model.deleted_at == None
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_tasks_by_title_or_description(self, search_term: str):
        stmt = select(self.model).where(
            (self.model.title.ilike(f"%{search_term}%")) |
            (self.model.description.ilike(f"%{search_term}%")),
            self.model.deleted_at == None
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_tasks_by_status(self, status: str):
        stmt = select(self.model).where(
            self.model.status == status,
            self.model.deleted_at == None
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_tasks_by_status_and_priority_from_project(self, status: str, priority: str, project_id: int):
        stmt = select(self.model).where(
            self.model.status == status,
            self.model.priority == priority,
            self.model.project_id == project_id,
            self.model.parent_id == None,
            self.model.deleted_at == None
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_subtasks(self, task_id: int):
        stmt = select(self.model).where(
            self.model.parent_id == task_id,
            self.model.deleted_at == None
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_open_subtasks(self, task_id: int):
        stmt = select(self.model).where(
            self.model.parent_id == task_id,
            self.model.status != TaskStatus.DONE,
            self.model.deleted_at == None
        )
        result = await self.db.execute(stmt)
        return len(result.scalars().all())
