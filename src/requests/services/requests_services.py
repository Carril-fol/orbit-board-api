from collaborators.interfaces import ICollaboratorService
from project_invitations.repositories.project_invitation_repository import ProjectInvitationRepository
from projects.repositories.project_repository import ProjectRepository
from projects.models.project import Project

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
    RequestProjectNotFoundError,
    RequestAlreadyExists,
    RequestAlreadyRespondedError,
    RequestNotFound,
    RequestUserAlreadyIsInvited
)


class RequestsService:
    def __init__(
        self,
        requests_repository: RequestsRepository,
        project_repository: ProjectRepository,
        project_invitations_repo: ProjectInvitationRepository,
        collaborator_service: ICollaboratorService
    ):
        self.requests_repository = requests_repository
        self.project_repository = project_repository
        self.project_invitations_repo = project_invitations_repo
        self.collaborator_service = collaborator_service

    def _ensure_is_owner(self, project: Project, user_id: int) -> None:
        if project.owner_id != int(user_id):
            raise PermissionError("Only the project owner can perform this action")

    async def _get_project_or_raise(self, project_id: int) -> Project:
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise RequestProjectNotFoundError()
        
        return project

    async def _validate_if_exists(self, user_id: int, project_id: int) -> None:
        request = await self.requests_repository.get_request_by_user_id_and_project_id(user_id, project_id)
        if request:
            raise RequestAlreadyExists()
    
    async def create_request(
        self,
        data: RegisterRequestsInputSchema,
        user_id: int,
        project_id: int,
    ) -> None:
        await self._validate_if_exists(user_id, project_id)

        project_invitations = await self.project_invitations_repo.get_project_invitation_by_project_id_and_user_id(project_id, user_id)
        if project_invitations:
            raise RequestUserAlreadyIsInvited()

        project = await self._get_project_or_raise(project_id)

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

        project = await self._get_project_or_raise(request.project_id)

        self._ensure_is_owner(project, user_id)

        if accepted:
            request.status = RequestStatus.APPROVED
            await self.collaborator_service.add_member_to_project(
                id_user=request.user_id,
                id_project=project.id,
                role=request.role
            )
        else:
            request.status = RequestStatus.REJECTED

        await self.requests_repository.update(request)

    async def get_all_requests(self, project_id: int, user_id: int) -> list[DetailRequestSchema]:
        project = await self._get_project_or_raise(project_id)

        self._ensure_is_owner(project, user_id)

        requests = await self.requests_repository.get_requests_by_project_id(project_id)
        return [DetailRequestSchema.model_validate(request) for request in requests]

    async def get_request(self, request_id: int, user_id: int) -> DetailRequestSchema:
        request = await self.requests_repository.get_request_by_id(request_id)
        if not request:
            raise RequestNotFound()

        project = await self._get_project_or_raise(request.project_id)

        self._ensure_is_owner(project, user_id)

        return DetailRequestSchema.model_validate(request)
