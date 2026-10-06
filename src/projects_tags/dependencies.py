from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from projects.dependencies import get_project_authorization_service
from projects.interfaces import IProjectAuthorizationService
from audit_logs.dependencies import get_audit_log_service
from audit_logs.interfaces import IAuditLogService
from shared.database import get_async_db

from .interfaces import IProjectTagService
from .repositories.project_tag_repository import ProjectTagRepository
from .services.project_tag_service import ProjectTagService


def get_project_tag_repository(db: AsyncSession = Depends(get_async_db, scope="function")) -> ProjectTagRepository:
    return ProjectTagRepository(db)


def get_project_tag_service(
    repo: ProjectTagRepository = Depends(get_project_tag_repository),
    audit_log_service: IAuditLogService = Depends(get_audit_log_service),
    project_authorization_service: IProjectAuthorizationService = Depends(get_project_authorization_service)
) -> IProjectTagService:
    return ProjectTagService(repo, audit_log_service, project_authorization_service)
