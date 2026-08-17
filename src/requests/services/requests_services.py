from collaborators.interfaces import ICollaboratorService
from project_invitations.interfaces import IProjectInvitationService
from projects.interfaces import IProjectService, IProjectAuthorizationService

from ..models.requests_model import Request
from ..repositories.requests_repository import RequestsRepository
from ..schemas.requests_schemas import (
    CreateRequestSchema,
    DetailRequestSchema,
    RegisterRequestsInputSchema,
    RequestStatus,
)
from ..exceptions import (
    RequestCollaboratorAlreadyExists,
    RequestAlreadyExists,
    RequestAlreadyRespondedError,
    RequestNotFound,
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
        project_authorization_service: IProjectAuthorizationService
    ):
        self.requests_repository = requests_repository
        self.project_service = project_service
        self.project_invitation_service = project_invitation_service
        self.collaborator_service = collaborator_service
        self.project_authorization_service = project_authorization_service

    async def _validate_if_exists(self, user_id: int, project_id: int) -> None:
        request = await self.requests_repository.get_request_by_user_id_and_project_id(user_id, project_id)
        if request and request.status in (RequestStatus.PENDING, RequestStatus.APPROVED):
            raise RequestAlreadyExists()

    async def create_request(
        self,
        data: RegisterRequestsInputSchema,
        user_id: int,
        project_id: int,
    ) -> None:
        await self._validate_if_exists(user_id, project_id)

        project_invitations = await self.project_invitation_service.get_invitation_by_project_and_user(project_id, user_id)
        if project_invitations:
            raise RequestUserAlreadyIsInvited()

        project = await self.project_service.get_project_by_id(project_id)

        user_exists = await self.collaborator_service.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if user_exists:
            raise RequestCollaboratorAlreadyExists()

        create_request = CreateRequestSchema(
            **data.model_dump(),
            user_id=user_id,
            project_id=project.id
        )

        request = Request(**create_request.model_dump())
        await self.requests_repository.create(request)

    async def respond_request(self, request_id: int, user_id: int, accepted: bool) -> None:
        request = await self.requests_repository.get_request_by_id(request_id)
        if not request:
            raise RequestNotFound()

        if request.status != RequestStatus.PENDING:
            raise RequestAlreadyRespondedError()

        await self.project_authorization_service.require_project_owner(user_id, request.project_id)

        if accepted:
            request.status = RequestStatus.APPROVED
            await self.collaborator_service.add_member_to_project(
                id_user=request.user_id,
                id_project=request.project_id,
                role=request.role
            )
        else:
            request.status = RequestStatus.REJECTED

        await self.requests_repository.update(request)

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
