from datetime import datetime, timezone

from audit_logs.interfaces import IAuditLogService

from collaborators.interfaces import ICollaboratorService

from tasks.models.task_model import Task
from tasks.repositories.task_repository import TaskRepository

from ..interfaces import ITaskUserService
from ..exceptions import (
    TaskUserAlreadyStatusAssigned,
    TaskUserIsNotAnCollaborator,
    TaskUserNotFound,
)
from ..models.task_user_model import TaskUser, TaskUserStatus
from ..repositories.task_user_repository import TaskUserRepository


class TaskUserService(ITaskUserService):

    def __init__(
        self,
        task_user_repo: TaskUserRepository,
        collaborator_service: ICollaboratorService,
        task_repo: TaskRepository,
        audit_log_service: IAuditLogService,
    ):
        self.repo = task_user_repo
        self.collaborator_service = collaborator_service
        self.task_repo = task_repo
        self.audit_log_service = audit_log_service

    async def _get_task_or_raise(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskUserNotFound()
        return task

    async def _get_task_user_or_raise(self, task_id: int, user_id: int) -> TaskUser:
        task_user = await self.repo.get_task_user_by_task_id_and_user_id(task_id, user_id)
        if not task_user:
            raise TaskUserNotFound()
        return task_user

    async def assign_user_to_task(self, task_id: int, target_user_id: int, actor_user_id: int ) -> None:
        task = await self._get_task_or_raise(task_id)

        await self.collaborator_service.require_project_owner(
            actor_user_id,
            task.project_id,
        )

        target_collaborator = await self.collaborator_service.get_collaborator_by_user_id_and_project_id(
            target_user_id,
            task.project_id,
        )
        if not target_collaborator:
            raise TaskUserIsNotAnCollaborator()

        await self.repo.assign_user(task_id, target_user_id,)

        await self.audit_log_service.record_diff(
            user_id=actor_user_id,
            entity_type="TaskUser",
            entity_id=task_id,
            action="assign_user",
            old_state={
                "user_id": None,
            },
            new_state={
                "user_id": target_user_id,
            },
        )

    async def unassign_user_from_task(self, task_id: int, target_user_id: int, actor_user_id: int) -> None:
        task = await self._get_task_or_raise(task_id)

        await self.collaborator_service.require_project_owner(
            actor_user_id,
            task.project_id,
        )

        task_user = await self._get_task_user_or_raise(
            task_id,
            target_user_id,
        )

        if task_user.status == TaskUserStatus.UNASSIGNED:
            raise TaskUserAlreadyStatusAssigned()

        task_user.status = TaskUserStatus.UNASSIGNED
        task_user.updated_at = datetime.now(timezone.utc)

        await self.repo.update(task_user)

        await self.audit_log_service.record_diff(
            user_id=actor_user_id,
            entity_type="TaskUser",
            entity_id=task_id,
            action="unassign_user",
            old_state={
                "user_id": target_user_id,
                "status": TaskUserStatus.ASSIGNED.value,
            },
            new_state={
                "user_id": target_user_id,
                "status": TaskUserStatus.UNASSIGNED.value,
            },
        )