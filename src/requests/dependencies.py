from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from collaborators.interfaces import ICollaboratorService
from collaborators.repositories.collaborator_repository import CollaboratorRepository
from collaborators.services.collaborators_service import CollaboratorService

from project_invitations.repositories.project_invitation_repository import ProjectInvitationRepository
from projects.repositories.project_repository import ProjectRepository

from .repositories.requests_repository import RequestsRepository
from .services.requests_services import RequestsService


def get_project_invitation_repository(
    db: AsyncSession = Depends(get_async_db),
) -> ProjectInvitationRepository:
    return ProjectInvitationRepository(db)


def get_project_repository(
    db: AsyncSession = Depends(get_async_db),
) -> ProjectRepository:
    return ProjectRepository(db)


def get_collaborator_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CollaboratorRepository:
    return CollaboratorRepository(db)


def get_requests_repository(
    db: AsyncSession = Depends(get_async_db),
) -> RequestsRepository:
    return RequestsRepository(db)


def get_collaborator_service(
    collaborator_repo: CollaboratorRepository = Depends(get_collaborator_repository),
    project_repo: ProjectRepository = Depends(get_project_repository)
) -> ICollaboratorService:
    return CollaboratorService(
        collaborator_repo,
        project_repo,
    )


def get_requests_service(
    repo: RequestsRepository = Depends(get_requests_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    project_invitation_repo: ProjectInvitationRepository = Depends(get_project_invitation_repository),
    collaborator_service: ICollaboratorService = Depends(get_collaborator_service)
) -> RequestsService:
    return RequestsService(
        repo,
        project_repo,
        project_invitation_repo,
        collaborator_service,
    )