from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from projects.authorization_dependencies import get_project_authorization_service
from projects.interfaces import IProjectAuthorizationService

from audit_logs.dependencies import get_audit_log_service
from audit_logs.interfaces import IAuditLogService

from .interfaces import ICollaboratorService
from .repositories.collaborator_repository import CollaboratorRepository
from .services.collaborators_service import CollaboratorService


def get_collaborators_repository(db: AsyncSession = Depends(get_async_db)) -> CollaboratorRepository:
    return CollaboratorRepository(db)


def get_collaborators_service(
    repo: CollaboratorRepository = Depends(get_collaborators_repository),
    audit_log_service: IAuditLogService = Depends(get_audit_log_service),
    project_authorization_service: IProjectAuthorizationService = Depends(get_project_authorization_service),
) -> ICollaboratorService:
    return CollaboratorService(repo, audit_log_service, project_authorization_service)