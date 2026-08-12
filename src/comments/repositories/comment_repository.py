from sqlalchemy import select, func, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from shared.database.base_repository import BaseRepository
from ..models.comment_model import Comment
from tasks.models.task_model import Task
from collaborators.models.collaborators_model import Collaborators


class CommentRepository(BaseRepository[Comment]):

    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)

    async def get_comments_by_task_id(self, task_id: int, limit: int = 20, offset: int = 0):
        stmt = select(Comment).where(Comment.task_id == task_id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_comments_count_by_task_id(self, task_id: int):
        stmt = select(func.count(Comment.id)).where(Comment.task_id == task_id)
        result = await self.db.execute(stmt)
        return result.scalar()

    async def verify_user_access_to_task(self, user_id: int, task_id: int) -> bool:
        stmt = select(exists().where(
            Collaborators.id_user == user_id,
            Collaborators.id_project == Task.project_id,
            Task.id == task_id
        ))
        result = await self.db.execute(stmt)
        return result.scalar()
