from ..interfaces import IProjectAuthorizationService

from ..exceptions.project_exception import (
    ProjectInsufficientPrivileges,
    ProjectNotFoundError,
)
from ..models.project import Project
from ..repositories.project_repository import ProjectRepository


class ProjectAuthorizationService(IProjectAuthorizationService):
    """
    Single source of truth for project ownership.

    Ownership is project.owner_id, never collaborator.role. The role column
    describes what a collaborator does on the project (backend, devops, ...),
    not what they are allowed to do, so it must not drive authorization.
    """

    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    async def require_project_owner(self, user_id: int, project_id: int) -> Project:
        project = await self.project_repo.get_project_by_id(project_id)

        if not project:
            raise ProjectNotFoundError("Project not found")

        if int(project.owner_id) != int(user_id):
            raise ProjectInsufficientPrivileges()

        return project
