from datetime import datetime, timezone

from audit_logs.services.audit_log_service import AuditLogService

from collaborators.repositories.collaborator_repository import CollaboratorRepository
from collaborators.models.collaborators_model import Collaborators

from tasks.models.task_model import Task
from tasks.repositories.task_repository import TaskRepository

from ..repositories.task_user_repository import TaskUserRepository
from ..models.task_user_model import TaskUserStatus, TaskUser
from ..exceptions import (
    TaskUserHasNotPermission,
    TaskUserAlreadyStatusAssigned,
    TaskUserIsNotAnCollaborator,
    TaskUserNotFound
)


class TaskUserService:
    
    def __init__(
        self, 
        task_user_repo: TaskUserRepository, 
        collaborator_repo: CollaboratorRepository, 
        task_repo: TaskRepository, 
        audit_log_service: AuditLogService
    ):
        self.repo = task_user_repo
        self.collaborator_repo = collaborator_repo
        self.task_repo = task_repo
        self.audit_log_service = audit_log_service
    
    def _require_project_owner(self, project_id: int, user_id: int) -> Collaborators:
        collaborator = self.collaborator_repo.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if not collaborator:
            raise TaskUserIsNotAnCollaborator()
        if collaborator.role != "OWNER":
            raise TaskUserHasNotPermission()
        return collaborator
    
    def assign_user_to_task(self, task_id: int, target_user_id: int, actor_user_id: int) -> None:
        task: Task = self.task_repo.get_by_id(task_id)
        
        actor_collab: Collaborators = self.collaborator_repo.get_collaborator_by_user_id_and_project_id(actor_user_id, task.project_id)
        if not actor_collab or actor_collab.role != "OWNER":
            raise TaskUserHasNotPermission()

        target_collab: Collaborators = self.collaborator_repo.get_collaborator_by_user_id_and_project_id(target_user_id, task.project_id)
        if not target_collab:
            raise TaskUserIsNotAnCollaborator()
        
        self.repo.assign_user(task_id, target_user_id)

        self.audit_log_service.record_diff(
            user_id=actor_user_id,
            entity_type="TaskUser",
            entity_id=task_id,
            action="assign_user",
            old_state={
                "user_id": None
            },
            new_state={
                "user_id": target_user_id
            }
        )

    def unassign_user_from_task(self, task_id: int, target_user_id: int, actor_user_id: int) -> None:
        task: Task = self.task_repo.get_by_id(task_id)
        
        self._require_project_owner(task.project_id, actor_user_id)
        
        task_user: TaskUser = self.repo.get_task_user_by_task_id_and_user_id(task_id, target_user_id)
            
        if not task_user:
            raise TaskUserNotFound()
            
        if task_user.status == TaskUserStatus.UNASSIGNED:
            raise TaskUserAlreadyStatusAssigned()
            
        task_user.status = TaskUserStatus.UNASSIGNED
        task_user.updated_at = datetime.now(timezone.utc)

        self.repo.update(task_user)

        self.audit_log_service.record_diff(
            user_id=actor_user_id,
            entity_type="TaskUser",
            entity_id=task_id,
            action="unassign_user",
            old_state={
                "user_id": target_user_id,
                "status": TaskUserStatus.ASSIGNED.value
            },
            new_state={
                "user_id": target_user_id,
                "status": TaskUserStatus.UNASSIGNED.value
            }
        )