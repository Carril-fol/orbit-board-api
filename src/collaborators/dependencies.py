from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from projects.repositories.project_repository import ProjectRepository
from shared.database import get_async_db

from .interfaces import ICollaboratorService
from .repositories.collaborator_repository import CollaboratorRepository
from .services.collaborators_service import CollaboratorService


def get_collaborators_repository(db: AsyncSession = Depends(get_async_db)) -> CollaboratorRepository:
    return CollaboratorRepository(db)


def get_project_repository(db: AsyncSession = Depends(get_async_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_collaborators_service(
    db: AsyncSession = Depends(get_async_db),
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> ICollaboratorService:
    collaborator_repo = CollaboratorRepository(db)
    return CollaboratorService(collaborator_repo, project_repo)
