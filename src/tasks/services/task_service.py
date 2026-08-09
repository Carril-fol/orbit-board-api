from datetime import datetime, timezone

from collaborators.repositories.collaborator_repository import CollaboratorRepository
from audit_logs.services.audit_log_service import AuditLogService

from ..repositories.task_repository import TaskRepository
from ..models.task_model import Task
from ..models.task_user_model import TaskUserStatus
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
    TaskUserIsNotAnCollaborator,
    TaskCannotCompleted
)


class TaskService:

    def __init__(
        self, 
        repo: TaskRepository, 
        collaborator_repo: CollaboratorRepository,
        audit_log_service: AuditLogService
    ):
        self.repo = repo
        self.collaborator_repo = collaborator_repo
        self.audit_log_service = audit_log_service

    def _format_tasks(self, tasks):
        tasks_formatted = [
            DetailTaskOutputSchema.model_validate(task)
            for task in tasks
        ]
        return ListDetailTaskOutputSchema(tasks=tasks_formatted)

    def _get_task(self, task_id: int):
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFound()
        return task

    def _require_project_owner(self, project_id: int, user_id: int):
        collaborator = self.collaborator_repo.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if not collaborator:
            raise TaskUserIsNotAnCollaborator()
        if collaborator.role != "OWNER":
            raise TaskUserHasNotPermission()
        return collaborator

    def create(self, data: RegisterTaskInputSchema, user_id: int, project_id: int):
        collaborator = self.collaborator_repo.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if not collaborator:
            raise TaskUserHasNotPermission()

        if data.parent_id:
            parent_task = self.repo.get_by_id(data.parent_id)
            if not parent_task:
                raise TaskNotFound()
            if parent_task.project_id != project_id:
                raise TaskUserHasNotPermission()

        task_data = data.model_dump()
        task_data["project_id"] = project_id

        validated_data = CreateTaskInputSchema.model_validate(task_data)

        task_entity = Task(**validated_data.model_dump())
        self.repo.create(task_entity)

    def delete_task(self, task_id: int, user_id: int):
        task = self._get_task(task_id)
        self._require_project_owner(task.project_id, user_id)
        
        old_state = task.to_dict()
        
        task.deleted_at = datetime.now(timezone.utc)
        
        self.repo.update(task)

        new_state = task.to_dict()
        
        self.audit_log_service.record_diff(
            user_id,
            "Task",
            task.id,
            "delete_task",
            old_state,
            new_state
        )

    def update_task(self, task_id: int, data: UpdateTaskInputSchema, user_id: int):
        task = self._get_task(task_id)
        self._require_project_owner(task.project_id, user_id)
        
        old_state = task.to_dict()

        if data.status == "DONE":
            open_subtasks = self.repo.count_open_subtasks(task_id)
            if open_subtasks > 0:
                raise TaskCannotCompleted()

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
            
        new_state = task.to_dict()
        
        self.audit_log_service.record_diff(
            user_id,
            "Task",
            task.id,
            "update_task",
            old_state,
            new_state
        )
        
        self.repo.update(task)

    def get_task_by_id(self, task_id: int, user_id: int) -> DetailTaskOutputSchema:
        task = self._get_task(task_id)
        if not self.collaborator_repo.get_collaborator_by_user_id_and_project_id(user_id, task.project_id):
            raise TaskUserIsNotAnCollaborator()
        return DetailTaskOutputSchema.model_validate(task).model_dump()

    def get_tasks_by_project(self, user_id: int, project_id: int, status: str = None, priority: str = None, filter_user_id: int = None):
        if not self.collaborator_repo.get_collaborator_by_user_id_and_project_id(user_id, project_id):
            raise PermissionError("User is not a collaborator of the project")

        tasks_raw = self.repo.get_tasks_by_project(
            project_id=project_id,
            status=status,
            priority=priority,
            user_id=filter_user_id
        )
        tasks_formated = self._format_tasks(tasks_raw)
        return tasks_formated

    def get_tasks_from_user(self, user_id: int, project_id: int):
        tasks = self.repo.get_tasks_from_project_from_user(user_id, project_id)
        return self._format_tasks(tasks)

    def get_tasks_by_priority(self, priority: str):
        tasks = self.repo.get_tasks_with_priority(priority.upper())
        return self._format_tasks(tasks)

    def get_tasks_by_title_or_description(self, search_term: str):
        tasks = self.repo.get_tasks_by_title_or_description(search_term)
        return self._format_tasks(tasks)

    def get_tasks_by_status(self, status: str):
        tasks = self.repo.get_tasks_by_status(status.upper())
        return self._format_tasks(tasks)
    