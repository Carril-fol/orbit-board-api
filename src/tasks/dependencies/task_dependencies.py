from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db
from collaborators.repositories.collaborator_repository import CollaboratorRepository

from audit_logs.repositories.audit_log_repository import AuditLogRepository
from audit_logs.services.audit_log_service import AuditLogService

from ..repositories.task_repository import TaskRepository
from ..services.task_service import TaskService

def get_audit_log_repository(
    db: AsyncSession = Depends(get_async_db),
) -> AuditLogRepository:
    return AuditLogRepository(db)


def get_collaborator_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CollaboratorRepository:
    return CollaboratorRepository(db)


def get_task_repository(
    db: AsyncSession = Depends(get_async_db),
) -> TaskRepository:
    return TaskRepository(db)


def get_task_repository_alt(
    db: AsyncSession = Depends(get_async_db),
) -> TaskRepository:
    return TaskRepository(db)


def get_audit_log_service(
    repo: AuditLogRepository = Depends(get_task_repository),
):
    return AuditLogService(repo)


def get_task_service(
    repo: TaskRepository = Depends(get_task_repository),
    collaborator_repo: CollaboratorRepository = Depends(get_collaborator_repository),
    audit_log_service: AuditLogService = Depends(get_audit_log_service)
) -> TaskService:
    return TaskService(repo, collaborator_repo, audit_log_service)
