from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from projects.dependencies import get_project_repository
from projects.repositories.project_repository import ProjectRepository
from shared.database import get_async_db

from .repositories.project_tag_repository import ProjectTagRepository
from .services.project_tag_service import ProjectTagService


def get_project_tag_repository(
    db: AsyncSession = Depends(get_async_db),
) -> ProjectTagRepository:
    return ProjectTagRepository(db)


def get_project_tag_service(
    repo: ProjectTagRepository = Depends(get_project_tag_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
):
    return ProjectTagService(repo, project_repo)
