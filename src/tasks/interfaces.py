from abc import ABC, abstractmethod

from .models.task_model import Task
from .schemas.task_schemas import (
    RegisterTaskInputSchema,
    DetailTaskOutputSchema,
    ListDetailTaskOutputSchema,
    UpdateTaskInputSchema,
)


class ITaskService(ABC):

    @abstractmethod
    async def get_task_or_raise(self, task_id: int) -> Task:
        """Return the task entity, or raise if it does not exist. No permission check."""
        pass

    @abstractmethod
    async def create(self, data: RegisterTaskInputSchema, user_id: int, project_id: int):
        pass

    @abstractmethod
    async def update_task(self, task_id: int, data: UpdateTaskInputSchema, user_id: int):
        pass

    @abstractmethod
    async def delete_task(self, task_id: int, user_id: int):
        pass

    @abstractmethod
    async def get_task_by_id(self, task_id: int, user_id: int) -> DetailTaskOutputSchema:
        pass

    @abstractmethod
    async def get_tasks_by_project(
        self,
        user_id: int,
        project_id: int,
        status: str = None,
        priority: str = None,
        filter_user_id: int = None
    ) -> ListDetailTaskOutputSchema:
        pass

    @abstractmethod
    async def get_tasks_from_user(self, user_id: int, project_id: int) -> ListDetailTaskOutputSchema:
        pass


class ITaskUserService(ABC):

    @abstractmethod
    async def assign_user_to_task(self, task_id: int, target_user_id: int, actor_user_id: int) -> None:
        pass

    @abstractmethod
    async def unassign_user_from_task(self, task_id: int, target_user_id: int, actor_user_id: int) -> None:
        pass
