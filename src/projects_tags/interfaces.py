from abc import ABC, abstractmethod
from .schemas.project_tag_schema import RegisterProjectTagInputSchema

class IProjectTagService(ABC):
    @abstractmethod
    async def create_project_tag(self, id_project: int, data: RegisterProjectTagInputSchema, user_id: int) -> None:
        pass

    @abstractmethod
    async def delete_tag_from_project(self, id_tag: int, user_id: int) -> None:
        pass
