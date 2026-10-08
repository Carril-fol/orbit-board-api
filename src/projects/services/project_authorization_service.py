from ..interfaces import IProjectAuthorizationService

from ..exceptions import (
    ProjectInsufficientPrivileges,
    ProjectNotFoundError,
    ProjectIsFull
)
from ..models.project import Project
from ..repositories.project_repository import ProjectRepository


class ProjectAuthorizationService(IProjectAuthorizationService):

    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    async def get_project(self, project_id: int) -> Project:
        project = await self.project_repo.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()
        return project

    async def require_project_owner(self, user_id: int, project_id: int) -> Project:
        project = await self.get_project(project_id)

        if project.owner_id != user_id:
            raise ProjectInsufficientPrivileges()

        return project

    async def require_capacity_for(self, project_id: int, current_members: int) -> None:
        project = await self.get_project(project_id)

        if current_members >= project.max_collaborators:
            raise ProjectIsFull()