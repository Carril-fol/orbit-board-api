from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from collaborators.repositories.collaborator_repository import CollaboratorRepository
from project_invitations.repositories.project_invitation_repository import (
    ProjectInvitationRepository,
)
from projects.repositories.project_repository import ProjectRepository
from shared.database import get_async_db

from .repositories.requests_repository import RequestsRepository
from .services.requests_services import RequestsService


def get_project_invitation_repository(
    db: AsyncSession = Depends(get_async_db),
) -> ProjectInvitationRepository:
    return ProjectInvitationRepository(db)


def get_project_repository(db: AsyncSession = Depends(get_async_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_collaborator_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CollaboratorRepository:
    return CollaboratorRepository(db)


def get_requests_repository(db: AsyncSession = Depends(get_async_db)) -> RequestsRepository:
    return RequestsRepository(db)


def get_requests_service(
    repo: RequestsRepository = Depends(get_requests_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    collaborator_repo: CollaboratorRepository = Depends(get_collaborator_repository),
    project_invitation_repo: ProjectInvitationRepository = Depends(
        get_project_invitation_repository
    ),
) -> RequestsService:
    return RequestsService(
        repo,
        collaborator_repo,
        project_repo,
        project_invitation_repo,
    )
