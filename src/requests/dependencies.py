from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from collaborators.dependencies import get_collaborators_service
from collaborators.interfaces import ICollaboratorService

from project_invitations.dependencies import get_project_invitation_service
from project_invitations.interfaces import IProjectInvitationService

from projects.dependencies import get_project_service
from projects.interfaces import IProjectService

from .interfaces import IRequestsService
from .repositories.requests_repository import RequestsRepository
from .services.requests_services import RequestsService


def get_requests_repository(
    db: AsyncSession = Depends(get_async_db),
) -> RequestsRepository:
    return RequestsRepository(db)


def get_requests_service(
    repo: RequestsRepository = Depends(get_requests_repository),
    project_service: IProjectService = Depends(get_project_service),
    project_invitation_service: IProjectInvitationService = Depends(get_project_invitation_service),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service),
) -> IRequestsService:
    return RequestsService(
        repo,
        project_service,
        project_invitation_service,
        collaborator_service,
    )
