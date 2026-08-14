from fastapi import Depends

from collaborators.dependencies import get_collaborators_service
from collaborators.interfaces import ICollaboratorService

from .authorization_dependencies import (
    get_project_repository,
    get_project_authorization_service,
)
from .repositories.project_repository import ProjectRepository
from .services.project_service import ProjectService
from .interfaces import IProjectService, IProjectAuthorizationService


def get_project_service(
    repo: ProjectRepository = Depends(get_project_repository),
    collaborator_service: ICollaboratorService = Depends(get_collaborators_service),
    project_authorization_service: IProjectAuthorizationService = Depends(get_project_authorization_service)
) -> IProjectService:
    return ProjectService(repo, collaborator_service, project_authorization_service)
