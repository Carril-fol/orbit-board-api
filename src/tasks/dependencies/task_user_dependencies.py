from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from collaborators.repositories.collaborator_repository import CollaboratorRepository
from tasks.repositories.task_repository import TaskRepository

from audit_logs.repositories.audit_log_repository import AuditLogRepository
from audit_logs.services.audit_log_service import AuditLogService

from ..repositories.task_user_repository import TaskUserRepository
from ..services.task_user_service import TaskUserService


def get_task_user_repo(
    db: AsyncSession = Depends(get_async_db),
) -> TaskUserRepository:
    return TaskUserRepository(db)


def get_collaborator_repo(
    db: AsyncSession = Depends(get_async_db),
) -> CollaboratorRepository:
    return CollaboratorRepository(db)


def get_task_repo(
    db: AsyncSession = Depends(get_async_db),
) -> TaskRepository:
    return TaskRepository(db)


def get_audit_log_repo(
    db: AsyncSession = Depends(get_async_db),
) -> AuditLogRepository:
    return AuditLogRepository(db)


def get_audit_log_service(
    repo: AuditLogRepository = Depends(get_audit_log_repo),
) -> AuditLogService:
    return AuditLogService(repo)


def get_task_user_service(
    task_user_repo: TaskUserRepository = Depends(get_task_user_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
    collaborator_repo: CollaboratorRepository = Depends(get_collaborator_repo),
    audit_log_service: AuditLogService = Depends(get_audit_log_service),
) -> TaskUserService:
    return TaskUserService(
        task_user_repo=task_user_repo,
        task_repo=task_repo,
        collaborator_repo=collaborator_repo,
        audit_log_service=audit_log_service,
    )
