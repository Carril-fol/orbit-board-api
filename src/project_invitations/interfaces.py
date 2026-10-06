from abc import ABC, abstractmethod

from .models.project_invitation_model import ProjectInvitation
from .schemas.project_invitations_schemas import (
    CreateProjectInvitation,
    ListReceivedInvitationSchema,
)

class IProjectInvitationService(ABC):
    @abstractmethod
    async def get_pending_invitation(self, project_id: int, user_id: int) -> ProjectInvitation | None:
        pass

    @abstractmethod
    async def create_project_invitation(self, data: CreateProjectInvitation, inviter_id: int) -> str:
        pass

    @abstractmethod
    async def revoke_project_invitation(self, id_invite: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def respond_project_invitation(self, token: str, user_id: int, accepted: bool) -> None:
        pass

    @abstractmethod
    async def get_received_invitations(self, user_id: int) -> ListReceivedInvitationSchema:
        pass
