from datetime import datetime, timezone

from collaborators.interfaces import ICollaboratorService
from audit_logs.interfaces import IAuditLogService

from ..interfaces import ITaskService
from ..repositories.task_repository import TaskRepository
from ..models.task_model import Task
from ..schemas.task_schemas import (
    CreateTaskInputSchema, 
    ListDetailTaskOutputSchema, 
    RegisterTaskInputSchema, 
    DetailTaskOutputSchema, 
    UpdateTaskInputSchema,
)
from ..exceptions import (
    TaskNotFound,
    TaskUserHasNotPermission,
    TaskCannotCompleted
)


class TaskService(ITaskService):

    def __init__(
        self, 
        repo: TaskRepository,
        collaborator_service: ICollaboratorService,
        audit_log_service: IAuditLogService
    ):
        self.repo = repo
        self.collaborator_service = collaborator_service
        self.audit_log_service = audit_log_service

    def _format_tasks(self, tasks):
        tasks_formatted = [
            DetailTaskOutputSchema.model_validate(task)
            for task in tasks
        ]
        return ListDetailTaskOutputSchema(tasks=tasks_formatted)

    async def get_task_or_raise(self, task_id: int) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFound()
        return task

    async def create(self, data: RegisterTaskInputSchema, user_id: int, project_id: int):
        await self.collaborator_service.require_project_member(user_id, project_id)

        if data.parent_id:
            parent_task = await self.repo.get_by_id(data.parent_id)
            if not parent_task:
                raise TaskNotFound()
            if parent_task.project_id != project_id:
                raise TaskUserHasNotPermission()

        task_data = data.model_dump()
        task_data["project_id"] = project_id

        validated_data = CreateTaskInputSchema.model_validate(task_data)

        task_entity = Task(**validated_data.model_dump())
        await self.repo.create(task_entity)

    async def delete_task(self, task_id: int, user_id: int):
        task = await self.get_task_or_raise(task_id)
        await self.collaborator_service.require_project_owner(user_id, task.project_id)
        
        old_state = task.to_dict()
        
        task.deleted_at = datetime.now(timezone.utc)
        
        await self.repo.update(task)

        new_state = task.to_dict()
        
        await self.audit_log_service.record_diff(
            user_id,
            "Task",
            task.id,
            "delete_task",
            old_state,
            new_state
        )

    async def update_task(self, task_id: int, data: UpdateTaskInputSchema, user_id: int):
        task = await self.get_task_or_raise(task_id)
        await self.collaborator_service.require_project_owner(user_id, task.project_id)
        
        old_state = task.to_dict()

        if data.status == "DONE":
            open_subtasks = await self.repo.count_open_subtasks(task_id)
            if open_subtasks > 0:
                raise TaskCannotCompleted()

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
            
        new_state = task.to_dict()
        
        await self.audit_log_service.record_diff(
            user_id,
            "Task",
            task.id,
            "update_task",
            old_state,
            new_state
        )
        
        await self.repo.update(task)

    async def get_task_by_id(self, task_id: int, user_id: int) -> DetailTaskOutputSchema:
        task = await self.get_task_or_raise(task_id)
        await self.collaborator_service.require_project_member(user_id, task.project_id)
        return DetailTaskOutputSchema.model_validate(task).model_dump()

    async def get_tasks_by_project(self, user_id: int, project_id: int, status: str = None, priority: str = None, filter_user_id: int = None) -> ListDetailTaskOutputSchema:
        await self.collaborator_service.require_project_member(user_id, project_id)

        tasks_raw = await self.repo.get_tasks_by_project(
            project_id=project_id,
            status=status,
            priority=priority,
            user_id=filter_user_id
        )
        tasks_formated = self._format_tasks(tasks_raw)
        return tasks_formated

    async def get_tasks_from_user(self, user_id: int, project_id: int):
        tasks = await self.repo.get_tasks_from_project_from_user(user_id, project_id)
        return self._format_tasks(tasks)

    async def get_tasks_by_priority(self, priority: str):
        tasks = await self.repo.get_tasks_with_priority(priority.upper())
        return self._format_tasks(tasks)

    async def get_tasks_by_title_or_description(self, search_term: str):
        tasks = await self.repo.get_tasks_by_title_or_description(search_term)
        return self._format_tasks(tasks)

    async def get_tasks_by_status(self, status: str):
        tasks = await self.repo.get_tasks_by_status(status.upper())
        return self._format_tasks(tasks)
    