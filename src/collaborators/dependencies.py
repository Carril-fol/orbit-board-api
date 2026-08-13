from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from .interfaces import ICollaboratorService
from .repositories.collaborator_repository import CollaboratorRepository
from .services.collaborators_service import CollaboratorService


def get_collaborators_repository(db: AsyncSession = Depends(get_async_db)) -> CollaboratorRepository:
    return CollaboratorRepository(db)


def get_collaborators_service(
    db: AsyncSession = Depends(get_async_db)
) -> ICollaboratorService:
    collaborator_repo = CollaboratorRepository(db)
    return CollaboratorService(collaborator_repo)