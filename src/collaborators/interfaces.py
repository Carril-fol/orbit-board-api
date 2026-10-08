from abc import ABC, abstractmethod

from .models.collaborators_model import Collaborators
from .schemas.collaborators_schema import (
    ListDetailCollaboratorsSchema,
    UpdateCollaboratorsSchema
)

class ICollaboratorService(ABC):

    @abstractmethod
    async def add_member_to_project(self, id_user: int, id_project: int, role: str, actor_id: int):
        pass

    @abstractmethod
    async def get_collaborators(self, id_project: int, user_id: int) -> ListDetailCollaboratorsSchema:
        pass

    @abstractmethod
    async def remove_collaborator(self, collaborator_id: int, user_id: int):
        pass

    @abstractmethod
    async def leave_project(self, project_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def change_role_collaborator(self, collaborator_id: int, data: UpdateCollaboratorsSchema, user_id: int):
        pass

    @abstractmethod
    async def get_collaborator_by_user_id_and_project_id(self, user_id: int, project_id: int) -> Collaborators | None:
        pass

    @abstractmethod
    async def count_project_collaborators(self, project_id: int) -> int:
        pass

    @abstractmethod
    async def get_project_ids_for_user(self, user_id: int) -> list[int]:
        pass

    @abstractmethod
    async def require_project_member(self, user_id: int, project_id: int) -> Collaborators:
        """Return the collaborator, or raise if the user does not belong to the project."""
        pass

