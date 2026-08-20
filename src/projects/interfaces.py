from abc import ABC, abstractmethod

from .models.project import Project
from .schemas.project_schema import (
    ProjectDetail,
    RegisterProjectInputSchema,
    UpdateProjectInputSchema,
    ListProjectDetail
)

class IProjectAuthorizationService(ABC):

    @abstractmethod
    async def require_project_owner(self, user_id: int, project_id: int) -> Project:
        pass

    @abstractmethod
    async def require_capacity_for(self, project_id: int, current_members: int) -> None:
        pass


class IProjectService(ABC):

    @abstractmethod
    async def get_project_by_id(self, id: int) -> Project:
        pass

    @abstractmethod
    async def create_project(self, data: RegisterProjectInputSchema, user_id: int):
        pass

    @abstractmethod
    async def detail_project_by_id(self, id: int, user_id: int) -> ProjectDetail:
        pass

    @abstractmethod
    async def update_project(self, id: int, data: UpdateProjectInputSchema, user_id: int):
        pass

    @abstractmethod
    async def delete_project(self, id: int, user_id: int):
        pass

    @abstractmethod
    async def get_all_project(self, per_page: int, page: int) -> ListProjectDetail:
        pass

    @abstractmethod
    async def get_projects_for_user(
        self, user_id: int, per_page: int, page: int
    ) -> ListProjectDetail:
        pass
