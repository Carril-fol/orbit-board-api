from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from collaborators.dependencies import get_collaborators_service
from collaborators.interfaces import ICollaboratorService
from projects.dependencies import get_project_authorization_service
from projects.interfaces import IProjectAuthorizationService
from audit_logs.dependencies import get_audit_log_service
from audit_logs.interfaces import IAuditLogService
from notifications.dependencies import get_notifications_service
from notifications.interfaces import INotificationService
from shared.database import get_async_db
from users.dependencies import get_user_service
from users.interfaces import IUserService

from .interfaces import IProjectInvitationService
from .repositories.project_invitation_repository import ProjectInvitationRepository
from .services.project_invitations_service import ProjectInvitationService


def get_project_invitation_repository(
    db: AsyncSession = Depends(get_async_db, scope="function"),
) -> ProjectInvitationRepository:
    return ProjectInvitationRepository(db)


def get_project_invitation_service(
    repository: ProjectInvitationRepository = Depends(
        get_project_invitation_repository
    ),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service),
    audit_log_service: IAuditLogService = Depends(get_audit_log_service),
    project_authorization_service: IProjectAuthorizationService = Depends(get_project_authorization_service),
    notification_service: INotificationService = Depends(get_notifications_service),
    user_service: IUserService = Depends(get_user_service),
) -> IProjectInvitationService:
    return ProjectInvitationService(
        repository,
        collaborator_service,
        audit_log_service,
        project_authorization_service,
        notification_service,
        user_service,
    )
