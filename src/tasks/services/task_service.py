from datetime import datetime, timezone

from collaborators.interfaces import ICollaboratorService
from audit_logs.interfaces import IAuditLogService
from projects.interfaces import IProjectAuthorizationService

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
    TaskCannotCompleted,
    TaskInvalidParent,
)


class TaskService(ITaskService):

    def __init__(
        self, 
        repo: TaskRepository,
        collaborator_service: ICollaboratorService,
        audit_log_service: IAuditLogService,
        project_authorization_service: IProjectAuthorizationService
    ):
        self.repo = repo
        self.collaborator_service = collaborator_service
        self.audit_log_service = audit_log_service
        self.project_authorization_service = project_authorization_service

    async def get_task_or_raise(self, task_id: int) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task or task.deleted_at != None:
            raise TaskNotFound()
        return task

    async def _validate_parent(self, parent_id: int, project_id: int, task_id: int | None = None) -> None:
        parent = await self.get_task_or_raise(parent_id)
        if parent.project_id != project_id:
            raise TaskUserHasNotPermission()
        if parent.parent_id is not None or parent.id == task_id:
            raise TaskInvalidParent()
        if task_id is not None and await self.repo.get_subtasks(task_id):
            raise TaskInvalidParent()

    async def create(self, data: RegisterTaskInputSchema, user_id: int, project_id: int):
        await self.collaborator_service.require_project_member(user_id, project_id)
        await self.project_authorization_service.require_open_project(project_id)

        if data.parent_id:
            await self._validate_parent(data.parent_id, project_id)

        task_data = data.model_dump()
        task_data["project_id"] = project_id

        validated_data = CreateTaskInputSchema.model_validate(task_data)

        task_entity = Task(**validated_data.model_dump())
        await self.repo.create(task_entity)

    async def delete_task(self, task_id: int, user_id: int):
        task = await self.get_task_or_raise(task_id)
        await self.project_authorization_service.require_project_owner(user_id, task.project_id)
        await self.project_authorization_service.require_open_project(task.project_id)

        task.deleted_at = datetime.now(timezone.utc)

        await self.repo.update(task)

        await self.audit_log_service.record_event(
            user_id=user_id,
            project_id=task.project_id,
            entity_type="Task",
            entity_id=task.id,
            action="delete_task",
            data=task.to_dict(),
        )

    async def update_task(self, task_id: int, data: UpdateTaskInputSchema, user_id: int):
        task = await self.get_task_or_raise(task_id)
        project = await self.project_authorization_service.get_project(task.project_id)
        fields = data.model_dump(exclude_unset=True)

        if project.owner_id != user_id:
            if fields.keys() - {"status"} or not await self.repo.is_assigned(task_id, user_id):
                raise TaskUserHasNotPermission()

        await self.project_authorization_service.require_open_project(task.project_id)

        if data.parent_id is not None:
            await self._validate_parent(data.parent_id, task.project_id, task_id)

        old_state = task.to_dict()

        if data.status == "DONE":
            open_subtasks = await self.repo.count_open_subtasks(task_id)
            if open_subtasks > 0:
                raise TaskCannotCompleted()

        for key, value in fields.items():
            setattr(task, key, value)
            
        new_state = task.to_dict()
        
        await self.audit_log_service.record_diff(
            user_id=user_id,
            project_id=task.project_id,
            entity_type="Task",
            entity_id=task.id,
            action="update_task",
            old_state=old_state,
            new_state=new_state,
        )
        
        await self.repo.update(task)

    async def get_task_by_id(self, task_id: int, user_id: int) -> DetailTaskOutputSchema:
        task = await self.repo.get_task_with_subtasks(task_id)
        if not task:
            raise TaskNotFound()
        await self.collaborator_service.require_project_member(user_id, task.project_id)
        return DetailTaskOutputSchema.model_validate(task)

    async def get_tasks_by_project(
        self,
        user_id: int,
        project_id: int,
        limit: int,
        offset: int,
        status: str = None,
        priority: str = None,
        filter_user_id: int = None
    ) -> ListDetailTaskOutputSchema:
        await self.collaborator_service.require_project_member(user_id, project_id)

        tasks, total = await self.repo.get_tasks_by_project(
            project_id=project_id,
            limit=limit,
            offset=offset,
            status=status,
            priority=priority,
            filter_user_id=filter_user_id
        )
        return ListDetailTaskOutputSchema(
            tasks=[DetailTaskOutputSchema.model_validate(task) for task in tasks],
            total=total,
            limit=limit,
            offset=offset,
        )