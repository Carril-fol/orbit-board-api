from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from projects.dependencies import get_project_authorization_service
from projects.interfaces import IProjectAuthorizationService
from shared.database import get_async_db

from .interfaces import IProjectTagService
from .repositories.project_tag_repository import ProjectTagRepository
from .services.project_tag_service import ProjectTagService


def get_project_tag_repository(db: AsyncSession = Depends(get_async_db)) -> ProjectTagRepository:
    return ProjectTagRepository(db)


def get_project_tag_service(
    repo: ProjectTagRepository = Depends(get_project_tag_repository),
    project_authorization_service: IProjectAuthorizationService = Depends(get_project_authorization_service)
) -> IProjectTagService:
    return ProjectTagService(repo, project_authorization_service)
