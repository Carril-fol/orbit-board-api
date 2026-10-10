from datetime import datetime, timedelta, timezone

from shared.config.settings import settings

from collaborators.interfaces import ICollaboratorService
from project_invitations.interfaces import IProjectInvitationService
from projects.interfaces import IProjectService, IProjectAuthorizationService
from projects.schemas.project_schema import ProjectVisibility
from audit_logs.interfaces import IAuditLogService
from notifications.interfaces import INotificationService
from notifications.models.notification_model import NotificationType

from ..models.requests_model import Request
from ..repositories.requests_repository import RequestsRepository
from ..schemas.requests_schemas import (
    CreateRequestSchema,
    DetailRequestSchema,
    RegisterRequestsInputSchema,
    RequestStatus,
    SentRequestSchema,
)
from ..exceptions import (
    RequestCollaboratorAlreadyExists,
    RequestAlreadyExists,
    RequestAlreadyRespondedError,
    RequestNotFound,
    RequestProjectNotFoundError,
    RequestRetryTooSoon,
    RequestUserAlreadyIsInvited
)
from ..interfaces import IRequestsService


class RequestsService(IRequestsService):
    def __init__(
        self,
        requests_repository: RequestsRepository,
        project_service: IProjectService,
        project_invitation_service: IProjectInvitationService,
        collaborator_service: ICollaboratorService,
        audit_log_service: IAuditLogService,
        project_authorization_service: IProjectAuthorizationService,
        notification_service: INotificationService,
    ):
        self.requests_repository = requests_repository
        self.project_service = project_service
        self.project_invitation_service = project_invitation_service
        self.collaborator_service = collaborator_service
        self.audit_log_service = audit_log_service
        self.project_authorization_service = project_authorization_service
        self.notification_service = notification_service

    async def _validate_if_exists(self, user_id: int, project_id: int) -> None:
        request = await self.requests_repository.get_request_by_user_id_and_project_id(user_id, project_id)
        if not request:
            return
        if request.status == RequestStatus.PENDING:
            raise RequestAlreadyExists()
        if request.status == RequestStatus.REJECTED:
            retry_at = request.review_at + timedelta(seconds=settings.request_retry_cooldown)
            if retry_at > datetime.now(timezone.utc):
                raise RequestRetryTooSoon()

    async def create_request(
        self,
        data: RegisterRequestsInputSchema,
        user_id: int,
        project_id: int,
    ) -> None:
        project = await self.project_service.get_project_by_id(project_id)
        if project.visibility != ProjectVisibility.PUBLIC:
            raise RequestProjectNotFoundError()
        await self.project_authorization_service.require_open_project(project.id)

        await self._validate_if_exists(user_id, project_id)

        if await self.project_invitation_service.get_pending_invitation(project_id, user_id):
            raise RequestUserAlreadyIsInvited()

        user_exists = await self.collaborator_service.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if user_exists:
            raise RequestCollaboratorAlreadyExists()

        create_request = CreateRequestSchema(
            **data.model_dump(),
            user_id=user_id,
            project_id=project.id
        )

        request = Request(**create_request.model_dump())
        request_created = await self.requests_repository.create(request)

        await self.audit_log_service.record_event(
            user_id=user_id,
            project_id=project.id,
            entity_type="Request",
            entity_id=request_created.id,
            action="create_request",
            data=request_created.to_dict(),
        )
        await self.notification_service.notify(
            user_id=project.owner_id,
            actor_id=user_id,
            type=NotificationType.REQUEST_RECEIVED,
            data={"request_id": request_created.id, "project_id": project.id},
        )

    async def respond_request(self, request_id: int, user_id: int, accepted: bool) -> None:
        request = await self.requests_repository.get_request_by_id(request_id)
        if not request:
            raise RequestNotFound()

        if request.status != RequestStatus.PENDING:
            raise RequestAlreadyRespondedError()

        await self.project_authorization_service.require_project_owner(user_id, request.project_id)

        old_state = request.to_dict()
        request.review_at = datetime.now(timezone.utc)

        if accepted:
            request.status = RequestStatus.APPROVED
            await self.collaborator_service.add_member_to_project(
                id_user=request.user_id,
                id_project=request.project_id,
                role=request.role,
                actor_id=user_id
            )
        else:
            request.status = RequestStatus.REJECTED

        await self.requests_repository.update(request)

        await self.audit_log_service.record_diff(
            user_id=user_id,
            project_id=request.project_id,
            entity_type="Request",
            entity_id=request.id,
            action="approve_request" if accepted else "decline_request",
            old_state=old_state,
            new_state=request.to_dict(),
        )
        await self.notification_service.notify(
            user_id=request.user_id,
            actor_id=user_id,
            type=NotificationType.REQUEST_APPROVED if accepted else NotificationType.REQUEST_DECLINED,
            data={"request_id": request.id, "project_id": request.project_id},
        )

    async def get_all_requests(self, project_id: int, user_id: int) -> list[DetailRequestSchema]:
        project = await self.project_authorization_service.require_project_owner(user_id, project_id)

        requests = await self.requests_repository.get_requests_by_project_id(project.id)
        return [DetailRequestSchema.model_validate(request) for request in requests]

    async def get_request(self, request_id: int, user_id: int) -> DetailRequestSchema:
        request = await self.requests_repository.get_request_by_id(request_id)
        if not request:
            raise RequestNotFound()

        await self.project_authorization_service.require_project_owner(user_id, request.project_id)

        return DetailRequestSchema.model_validate(request)

    async def get_sent_requests(self, user_id: int) -> list[SentRequestSchema]:
        requests = await self.requests_repository.get_requests_by_user_id(user_id)
        return [SentRequestSchema.model_validate(request) for request in requests]
