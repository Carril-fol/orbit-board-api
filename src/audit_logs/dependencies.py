from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from projects.authorization_dependencies import get_project_authorization_service
from projects.interfaces import IProjectAuthorizationService

from .interfaces import IAuditLogService
from .repositories.audit_log_repository import AuditLogRepository
from .services.audit_log_service import AuditLogService


def get_audit_log_repository(
    db: AsyncSession = Depends(get_async_db),
) -> AuditLogRepository:
    return AuditLogRepository(db)


def get_audit_log_service(
    repo: AuditLogRepository = Depends(get_audit_log_repository),
    project_authorization_service: IProjectAuthorizationService = Depends(get_project_authorization_service),
) -> IAuditLogService:
    return AuditLogService(repo, project_authorization_service)
