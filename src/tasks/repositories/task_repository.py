from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import exists, func, select

from shared.database.base_repository import BaseRepository
from ..models.task_model import Task, TaskStatus
from ..models.task_user_model import TaskUser, TaskUserStatus


LOAD_SUBTASKS = selectinload(Task.subtasks.and_(Task.deleted_at.is_(None)))


class TaskRepository(BaseRepository[Task]):

    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_task_with_subtasks(self, task_id: int):
        stmt = select(self.model).options(LOAD_SUBTASKS).where(
            self.model.id == task_id,
            self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tasks_by_project(
        self, project_id: int, limit: int = 20, offset: int = 0, status: str = None, priority: str = None, filter_user_id: int = None
    ) -> tuple[list[Task], int]:
        stmt = select(self.model).where(
            self.model.project_id == project_id,
            self.model.parent_id.is_(None),
            self.model.deleted_at.is_(None)
        )

        if status:
            stmt = stmt.where(self.model.status == status)
        if priority:
            stmt = stmt.where(self.model.priority == priority)
        if filter_user_id:
            stmt = stmt.join(TaskUser).where(
                TaskUser.user_id == filter_user_id,
                TaskUser.status == TaskUserStatus.ASSIGNED,
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.options(LOAD_SUBTASKS).order_by(self.model.id).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    async def is_assigned(self, task_id: int, user_id: int) -> bool:
        stmt = select(exists().where(
            TaskUser.task_id == task_id,
            TaskUser.user_id == user_id,
            TaskUser.status == TaskUserStatus.ASSIGNED,
        ))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_tasks_by_status_and_priority_from_project(self, status: str, priority: str, project_id: int):
        stmt = select(self.model).options(LOAD_SUBTASKS).where(
            self.model.status == status,
            self.model.priority == priority,
            self.model.project_id == project_id,
            self.model.parent_id.is_(None),
            self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_subtasks(self, task_id: int):
        stmt = select(self.model).where(
            self.model.parent_id == task_id,
            self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_open_subtasks(self, task_id: int) -> int:
        stmt = select(func.count()).select_from(self.model).where(
            self.model.parent_id == task_id,
            self.model.status != TaskStatus.DONE,
            self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
