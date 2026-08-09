from sqlalchemy import select

from shared.database.base_repository import BaseRepository

from ..models.task_user_model import TaskUser


class TaskUserRepository(BaseRepository[TaskUser]):

    def __init__(self, db):
        super().__init__(TaskUser, db)

    def assign_user(self, task_id: int, user_id: int):
        stmt = select(TaskUser).where(
            TaskUser.task_id == task_id,
            TaskUser.user_id == user_id
        )
        existing = self.db.execute(stmt).scalar_one_or_none()
        if existing:
            return existing

        assignment = TaskUser(task_id=task_id, user_id=user_id)
        super().create(assignment)
        return assignment
    
    def get_task_user_by_task_id_and_user_id(self, task_id: int, user_id: int):
        stmt = select(TaskUser).where(
            TaskUser.task_id == task_id,
            TaskUser.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()