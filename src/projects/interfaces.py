from abc import ABC, abstractmethod

from .schemas.project_schema import (
    ProjectDetail,
    RegisterProjectInputSchema,
    UpdateProjectInputSchema,
    ListProjectDetail
)

class IProjectService(ABC):
    
    @abstractmethod
    async def create_project(self, data: RegisterProjectInputSchema, user_id: int):
        pass
    
    @abstractmethod
    async def detail_project_by_id(self, id: int) -> ProjectDetail:
        pass
    
    @abstractmethod
    async def update_project(self, id: int, data: UpdateProjectInputSchema, user_id: int):
        pass
    
    @abstractmethod
    async def delete_project(self, id: int, user_id: int, data: dict):
        pass
    
    @abstractmethod
    async def get_all_project(self, per_page: int, page: int) -> ListProjectDetail:
        pass