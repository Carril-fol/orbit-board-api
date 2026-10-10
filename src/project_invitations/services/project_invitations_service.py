from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from shared.config.settings import settings

from collaborators.interfaces import ICollaboratorService
from projects.interfaces import IProjectAuthorizationService
from audit_logs.interfaces import IAuditLogService
from collaborators.exceptions import CollaboratorAlreadyExists
from users.interfaces import IUserService
from users.exceptions import UserNotFound
from notifications.interfaces import INotificationService
from notifications.models.notification_model import NotificationType

from ..exceptions import (
    ProjectInvitationPermissionError,
    ProjectInvitationAlreadyExistsError,
    ProjectInvitationNotFoundError,
    ProjectInvitationAlreadyResponded,
    ProjectInvitationExpired,
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
        collaborator_service: ICollaboratorService,
        audit_log_service: IAuditLogService,
        project_authorization_service: IProjectAuthorizationService,
        notification_service: INotificationService,
        user_service: IUserService,
    ):
        self.repository = repository
        self.collaborator_service = collaborator_service
        self.audit_log_service = audit_log_service
        self.project_authorization_service = project_authorization_service
        self.notification_service = notification_service
        self.user_service = user_service

    def _auditable_state(self, invite: ProjectInvitation) -> dict:
        state = invite.to_dict()
        state.pop("token")
        return state

    async def create_project_invitation(
        self,
        data: CreateProjectInvitation,
        inviter_id: int,
    ) -> str:
        project = await self.project_authorization_service.require_project_owner(inviter_id, data.id_project)

        invitee = await self.user_service.get_user_by_email(data.invitee_email)
        if not invitee:
            raise UserNotFound()

        if await self.collaborator_service.get_collaborator_by_user_id_and_project_id(invitee.id, project.id):
            raise CollaboratorAlreadyExists()

        collaborators_from_project = await self.collaborator_service.count_project_collaborators(project.id)
        await self.project_authorization_service.require_capacity_for(project.id, collaborators_from_project)

        if await self.repository.get_pending_invite(project.id, invitee.id):
            raise ProjectInvitationAlreadyExistsError()

        token = token_urlsafe(32)
        project_invitation_instance = ProjectInvitation(
            id_project=project.id,
            id_invitee=invitee.id,
            role=data.role,
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
        await self.notification_service.notify(
            user_id=invitation_created.id_invitee,
            actor_id=inviter_id,
            type=NotificationType.INVITATION_RECEIVED,
            data={"invitation_id": invitation_created.id, "project_id": project.id},
        )

        return token

    async def revoke_project_invitation(self, id_invite: int, user_id: int) -> None:
        invite = await self.repository.get_invite_by_id(id_invite)
        if not invite:
            raise ProjectInvitationNotFoundError()

        await self.project_authorization_service.require_project_owner(user_id, invite.id_project)

        if invite.status != InvitationStatus.PENDING:
            raise ProjectInvitationAlreadyResponded()

        old_state = self._auditable_state(invite)
        invite.status = InvitationStatus.REVOKED
        await self.repository.update(invite)

        await self.audit_log_service.record_diff(
            user_id=user_id,
            project_id=invite.id_project,
            entity_type="ProjectInvitation",
            entity_id=invite.id,
            action="revoke_invitation",
            old_state=old_state,
            new_state=self._auditable_state(invite),
        )
        await self.notification_service.notify(
            user_id=invite.id_invitee,
            actor_id=user_id,
            type=NotificationType.INVITATION_REVOKED,
            data={"invitation_id": invite.id, "project_id": invite.id_project},
        )

    async def respond_project_invitation(
        self,
        token: str,
        user_id: int,
        accepted: bool,
    ) -> None:
        invite = await self.repository.get_by_token(token)
        if not invite:
            raise ProjectInvitationNotFoundError()
        if invite.id_invitee != user_id:
            raise ProjectInvitationPermissionError()
        if invite.status == InvitationStatus.REVOKED:
            raise ProjectInvitationNotFoundError()

        if invite.status != InvitationStatus.PENDING:
            raise ProjectInvitationAlreadyResponded()

        if invite.created_at + timedelta(seconds=settings.invitation_expires) <= datetime.now(timezone.utc):
            raise ProjectInvitationExpired()

        old_state = self._auditable_state(invite)

        if accepted:
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
        await self.notification_service.notify(
            user_id=invite.id_inviter,
            actor_id=user_id,
            type=NotificationType.INVITATION_ACCEPTED if accepted else NotificationType.INVITATION_REJECTED,
            data={"invitation_id": invite.id, "project_id": invite.id_project},
        )

    async def get_received_invitations(self, user_id: int) -> ListReceivedInvitationSchema:
        invitations = await self.repository.get_pending_invitations_for_invitee(user_id)
        return ListReceivedInvitationSchema(
            invitations=[
                ReceivedInvitationSchema.model_validate(invitation)
                for invitation in invitations
            ]
        )

    async def get_pending_invitation(self, project_id: int, user_id: int) -> ProjectInvitation | None:
        return await self.repository.get_pending_invite(project_id, user_id)