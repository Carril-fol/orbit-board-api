"""
Providers for project authorization, kept apart from projects/dependencies.py.

get_project_service needs get_collaborators_service, and collaborators needs the
ownership check, so leaving both in the same module makes the two dependencies.py
files import each other. This module imports nothing outside projects, which lets
collaborators depend on it without closing the loop.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from .repositories.project_repository import ProjectRepository
from .services.project_authorization_service import ProjectAuthorizationService
from .interfaces import IProjectAuthorizationService


def get_project_repository(
    db: AsyncSession = Depends(get_async_db)
) -> ProjectRepository:
    return ProjectRepository(db)


def get_project_authorization_service(
    repo: ProjectRepository = Depends(get_project_repository)
) -> IProjectAuthorizationService:
    return ProjectAuthorizationService(repo)
