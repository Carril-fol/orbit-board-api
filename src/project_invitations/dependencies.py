from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from collaborators.dependencies import get_collaborators_service
from collaborators.interfaces import ICollaboratorService
from projects.dependencies import get_project_service, get_project_authorization_service
from projects.interfaces import IProjectService, IProjectAuthorizationService
from shared.database import get_async_db

from .interfaces import IProjectInvitationService
from .repositories.project_invitation_repository import ProjectInvitationRepository
from .services.project_invitations_service import ProjectInvitationService


def get_project_invitation_repository(
    db: AsyncSession = Depends(get_async_db),
) -> ProjectInvitationRepository:
    return ProjectInvitationRepository(db)


def get_project_invitation_service(
    repository: ProjectInvitationRepository = Depends(
        get_project_invitation_repository
    ),
    project_service: IProjectService = Depends(get_project_service),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service),
    project_authorization_service: IProjectAuthorizationService = Depends(get_project_authorization_service),
) -> IProjectInvitationService:
    return ProjectInvitationService(
        repository,
        project_service,
        collaborator_service,
        project_authorization_service,
    )
