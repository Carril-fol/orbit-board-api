from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from .interfaces import IAuditLogService
from .repositories.audit_log_repository import AuditLogRepository
from .services.audit_log_service import AuditLogService


def get_audit_log_repository(
    db: AsyncSession = Depends(get_async_db),
) -> AuditLogRepository:
    return AuditLogRepository(db)


def get_audit_log_service(
    repo: AuditLogRepository = Depends(get_audit_log_repository)
) -> IAuditLogService:
    return AuditLogService(repo)
