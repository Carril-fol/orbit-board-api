from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from collaborators.dependencies import get_collaborators_service
from collaborators.interfaces import ICollaboratorService

from audit_logs.dependencies import get_audit_log_service
from audit_logs.interfaces import IAuditLogService

from .interfaces import ITaskService, ITaskUserService
from .repositories.task_repository import TaskRepository
from .repositories.task_user_repository import TaskUserRepository
from .services.task_service import TaskService
from .services.task_user_service import TaskUserService


def get_task_repository(
    db: AsyncSession = Depends(get_async_db),
) -> TaskRepository:
    return TaskRepository(db)


def get_task_user_repository(
    db: AsyncSession = Depends(get_async_db),
) -> TaskUserRepository:
    return TaskUserRepository(db)


def get_task_service(
    repo: TaskRepository = Depends(get_task_repository),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service),
    audit_log_service: IAuditLogService = Depends(get_audit_log_service),
) -> ITaskService:
    return TaskService(repo, collaborator_service, audit_log_service)


def get_task_user_service(
    task_user_repo: TaskUserRepository = Depends(get_task_user_repository),
    task_repo: TaskRepository = Depends(get_task_repository),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service),
    audit_log_service: IAuditLogService = Depends(get_audit_log_service),
) -> ITaskUserService:
    return TaskUserService(
        task_user_repo=task_user_repo,
        task_repo=task_repo,
        collaborator_service=collaborator_service,
        audit_log_service=audit_log_service,
    )
