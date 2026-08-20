from secrets import token_urlsafe

from collaborators.interfaces import ICollaboratorService
from projects.interfaces import IProjectService, IProjectAuthorizationService
from audit_logs.interfaces import IAuditLogService

from ..exceptions import (
    ProjectInvitationPermissionError,
    ProjectInvitationAlreadyExistsError,
    ProjectInvitationNotFoundError,
    ProjectInvitationAlreadyResponded
)
from ..models.project_invitation_model import InvitationStatus, ProjectInvitation
from ..repositories.project_invitation_repository import ProjectInvitationRepository
from ..schemas.project_invitations_schemas import (
    CreateProjectInvitation,
    ListReceivedInvitationSchema,
    ReceivedInvitationSchema,
)
from ..interfaces import IProjectInvitationService


class ProjectInvitationService(IProjectInvitationService):
    def __init__(
        self,
        repository: ProjectInvitationRepository,
        project_service: IProjectService,
        collaborator_service: ICollaboratorService,
        audit_log_service: IAuditLogService,
        project_authorization_service: IProjectAuthorizationService,
    ):
        self.repository = repository
        self.project_service = project_service
        self.collaborator_service = collaborator_service
        self.audit_log_service = audit_log_service
        self.project_authorization_service = project_authorization_service

    def _auditable_state(self, invite: ProjectInvitation) -> dict:
        state = invite.to_dict()
        state.pop("token")
        return state

    async def get_received_invitations(self, user_id: int) -> ListReceivedInvitationSchema:
        invitations = await self.repository.get_pending_invitations_for_invitee(user_id)
        return ListReceivedInvitationSchema(
            invitations=[
                ReceivedInvitationSchema.model_validate(invitation)
                for invitation in invitations
            ]
        )

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
        invitation_created = await self.repository.create(project_invitation_instance)

        await self.audit_log_service.record_event(
            user_id=inviter_id,
            project_id=project.id,
            entity_type="ProjectInvitation",
            entity_id=invitation_created.id,
            action="create_invitation",
            data=self._auditable_state(invitation_created),
        )

        return token

    async def remove_project_invitation(self, id_invite: int, user_id: int):
        invite = await self.repository.get_invite_by_id(id_invite)
        if not invite:
            raise ProjectInvitationNotFoundError()
        if invite.id_inviter != user_id:
            raise ProjectInvitationPermissionError()

        deleted_state = self._auditable_state(invite)

        await self.repository.delete(id_invite)

        await self.audit_log_service.record_event(
            user_id=user_id,
            project_id=deleted_state["id_project"],
            entity_type="ProjectInvitation",
            entity_id=id_invite,
            action="remove_invitation",
            data=deleted_state,
        )

    async def respond_project_invitation(
        self,
        token: str,
        user_id: int,
        accepted: bool,
    ):
        invite = await self.repository.get_by_token(token)
        if not invite:
            raise ProjectInvitationNotFoundError()
        if invite.id_invitee != user_id:
            raise ProjectInvitationPermissionError()

        if (invite.status == InvitationStatus.ACCEPTED or invite.status == InvitationStatus.REJECTED):
            raise ProjectInvitationAlreadyResponded()
        
        old_state = self._auditable_state(invite)

        if accepted and invite.status == InvitationStatus.PENDING:
            await self.collaborator_service.add_member_to_project(
                id_user=user_id,
                id_project=invite.id_project,
                role=invite.role,
                actor_id=user_id,
            )

        invite.status = (InvitationStatus.ACCEPTED if accepted else InvitationStatus.REJECTED)
        await self.repository.update(invite)

        await self.audit_log_service.record_diff(
            user_id=user_id,
            project_id=invite.id_project,
            entity_type="ProjectInvitation",
            entity_id=invite.id,
            action="accept_invitation" if accepted else "reject_invitation",
            old_state=old_state,
            new_state=self._auditable_state(invite),
        )
