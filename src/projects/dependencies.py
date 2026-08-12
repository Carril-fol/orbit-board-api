from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from collaborators.dependencies import get_collaborators_service
from collaborators.interfaces import ICollaboratorService

from shared.database import get_async_db

from .repositories.project_repository import ProjectRepository
from .services.project_service import ProjectService
from .interfaces import IProjectService


def get_project_repository(db: AsyncSession = Depends(get_async_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_project_service(
    repo: ProjectRepository = Depends(get_project_repository),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service)
) -> IProjectService:
    return ProjectService(repo, collaborator_service)
