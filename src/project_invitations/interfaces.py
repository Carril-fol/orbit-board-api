from abc import ABC, abstractmethod
from .schemas.project_invitations_schemas import CreateProjectInvitation

class IProjectInvitationService(ABC):
    @abstractmethod
    async def get_invitation_by_project_and_user(self, project_id: int, user_id: int):
        pass

    @abstractmethod
    async def create_project_invitation(self, data: CreateProjectInvitation, inviter_id: int):
        pass

    @abstractmethod
    async def remove_project_invitation(self, id_invite: int, user_id: int):
        pass

    @abstractmethod
    async def respond_project_invitation(self, token: str, user_id: int, accepted: bool):
        pass
