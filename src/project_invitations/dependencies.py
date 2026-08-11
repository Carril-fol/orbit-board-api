from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from collaborators.dependencies import get_collaborators_repository
from collaborators.repositories.collaborator_repository import CollaboratorRepository
from projects.dependencies import get_project_repository
from projects.repositories.project_repository import ProjectRepository
from shared.database import get_async_db

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
    project_repo: ProjectRepository = Depends(get_project_repository),
    collaborator_repo: CollaboratorRepository = Depends(get_collaborators_repository),
):
    return ProjectInvitationService(repository, project_repo, collaborator_repo)
