from abc import ABC, abstractmethod
from .schemas.collaborators_schema import (
    ListDetailCollaboratorsSchema,
    UpdateCollaboratorsSchema
)

class ICollaboratorService(ABC):

    @abstractmethod
    async def add_member_to_project(self, id_user: int, id_project: int, role: str):
        pass

    @abstractmethod
    async def get_collaborators(self, id_project: int, user_id: int) -> ListDetailCollaboratorsSchema:
        pass

    @abstractmethod
    async def remove_collaborator(self, collaborator_id: int, user_id: int):
        pass

    @abstractmethod
    async def change_role_collaborator(self, collaborator_id: int, data: UpdateCollaboratorsSchema, user_id: int):
        pass

    @abstractmethod
    async def get_collaborator_by_user_id_and_project_id(self, project_id: int, user_id: int):
        pass