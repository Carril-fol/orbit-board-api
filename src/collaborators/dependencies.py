from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from projects.repositories.project_repository import ProjectRepository
from shared.database import get_async_db

from .repositories.collaborator_repository import CollaboratorRepository
from .services.collaborators_service import CollaboratorService


def get_collaborators_repository(
    db: AsyncSession = Depends(get_async_db),
):
    return CollaboratorRepository(db)


def get_collaborators_service(
    db: AsyncSession = Depends(get_async_db),
):
    collaborator_repo = CollaboratorRepository(db)
    project_repo = ProjectRepository(db)

    return CollaboratorService(collaborator_repo, project_repo)
