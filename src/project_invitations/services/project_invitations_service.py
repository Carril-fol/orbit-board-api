from secrets import token_urlsafe

from collaborators.interfaces import ICollaboratorService
from projects.interfaces import IProjectService, IProjectAuthorizationService

from ..exceptions import (
    ProjectInvitationPermissionError,
    ProjectInvitationAlreadyExistsError,
    ProjectInvitationNotFoundError,
    ProjectInvitationAlreadyResponded
)
from ..models.project_invitation_model import InvitationStatus, ProjectInvitation
from ..repositories.project_invitation_repository import ProjectInvitationRepository
from ..schemas.project_invitations_schemas import CreateProjectInvitation
from ..interfaces import IProjectInvitationService


class ProjectInvitationService(IProjectInvitationService):
    def __init__(
        self,
        repository: ProjectInvitationRepository,
        project_service: IProjectService,
        collaborator_service: ICollaboratorService,
        project_authorization_service: IProjectAuthorizationService,
    ):
        self.repository = repository
        self.project_service = project_service
        self.collaborator_service = collaborator_service
        self.project_authorization_service = project_authorization_service

    async def get_invitation_by_project_and_user(self, project_id: int, user_id: int):
        return await self.repository.get_project_invitation_by_project_id_and_user_id(project_id, user_id)

    async def _get_invite_already_exists_or_none(self, project_id: int, invitee_id: int):
        invite = await self.repository.get_invite_by_project_id_and_invitee_id(project_id, invitee_id)
        return invite

    async def create_project_invitation(
        self,
        data: CreateProjectInvitation,
        inviter_id: int,
    ):
        project = await self.project_authorization_service.require_project_owner(inviter_id, data.id_project)

        collaborators_from_project = await self.collaborator_service.count_project_collaborators(project.id)
        await self.project_authorization_service.require_capacity_for(project.id, collaborators_from_project)

        invite = await self._get_invite_already_exists_or_none(project.id, data.id_invitee)
        if invite and (
            invite.status == InvitationStatus.PENDING
            or invite.status == InvitationStatus.ACCEPTED
        ):
            raise ProjectInvitationAlreadyExistsError()

        token = token_urlsafe(32)
        project_invitation_instance = ProjectInvitation(
            **data.model_dump(), 
            id_inviter=inviter_id, 
            token=token
        )
        await self.repository.create(project_invitation_instance)
        return token

    async def remove_project_invitation(self, id_invite: int, user_id: int):
        invite = await self.repository.get_invite_by_id(id_invite)
        if not invite:
            raise ProjectInvitationNotFoundError()
        if int(invite.id_inviter) != int(user_id):
            raise ProjectInvitationPermissionError()
        await self.repository.delete(invite)

    async def respond_project_invitation(
        self,
        token: str,
        user_id: int,
        accepted: bool,
    ):
        invite = await self.repository.get_by_token(token)
        if not invite:
            raise ProjectInvitationNotFoundError()
        if int(invite.id_invitee) != int(user_id):
            raise ProjectInvitationPermissionError()

        if (invite.status == InvitationStatus.ACCEPTED or invite.status == InvitationStatus.REJECTED):
            raise ProjectInvitationAlreadyResponded()
        
        if accepted and invite.status == InvitationStatus.PENDING:
            await self.collaborator_service.add_member_to_project(
                id_user=user_id,
                id_project=invite.id_project,
                role=invite.role,
            )

        invite.status = (InvitationStatus.ACCEPTED if accepted else InvitationStatus.REJECTED)
        await self.repository.update(invite)
