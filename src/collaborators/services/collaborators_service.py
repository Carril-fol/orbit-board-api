from projects.interfaces import IProjectAuthorizationService

from ..interfaces import ICollaboratorService
from ..models.collaborators_model import Collaborators
from ..repositories.collaborator_repository import CollaboratorRepository
from ..schemas.collaborators_schema import (
    RegisterCollaboratorsInputSchema,
    DetailCollaboratorsSchema,
    ListDetailCollaboratorsSchema,
    UpdateCollaboratorsSchema
)
from ..exceptions import (
    CollaboratorAlreadyExists,
    CollaboratorNotAuthorized,
    CollaboratorNotFound
)


class CollaboratorService(ICollaboratorService):
    def __init__(
        self,
        repository: CollaboratorRepository,
        project_authorization_service: IProjectAuthorizationService,
    ):
        self.repository = repository
        self.project_authorization_service = project_authorization_service

    async def count_project_collaborators(self, project_id: int) -> int:
        collaborators = await self.repository.get_collaborators_from_project(project_id)
        return len(collaborators)

    async def require_project_member(self, user_id: int, project_id: int) -> Collaborators:
        collaborator = await self.repository.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if not collaborator:
            raise CollaboratorNotAuthorized()
        return collaborator

    async def add_member_to_project(self, id_user: int, id_project: int, role: str) -> Collaborators:
        already_member = await self.repository.get_collaborator_by_user_id_and_project_id(id_user, id_project)
        if already_member:
            raise CollaboratorAlreadyExists()

        collaborators: int = await self.count_project_collaborators(id_project)
        await self.project_authorization_service.require_capacity_for(id_project, collaborators)

        data = RegisterCollaboratorsInputSchema(role=role, id_user=id_user, id_project=id_project).model_dump()
        collaborator_entity = Collaborators(**data)
        await self.repository.create(collaborator_entity)

    async def get_collaborators(self, id_project: int, user_id: int) -> ListDetailCollaboratorsSchema:
        collaborators_raw = await self.repository.get_collaborators_from_project(id_project)

        user_ids: list[int] = [int(collaborator.id_user) for collaborator in collaborators_raw]

        if int(user_id) not in user_ids:
            raise CollaboratorNotAuthorized()

        collaborators_list: list[DetailCollaboratorsSchema] = [DetailCollaboratorsSchema.model_validate(collaborator) for collaborator in collaborators_raw]
        return ListDetailCollaboratorsSchema(collaborators=collaborators_list)

    async def remove_collaborator(self, collaborator_id: int, user_id: int):
        collaborator: Collaborators = await self.repository.get_by_id(collaborator_id)
        if not collaborator:
            raise CollaboratorNotFound()

        await self.project_authorization_service.require_project_owner(user_id, collaborator.id_project)
        await self.repository.delete(collaborator_id)

    async def change_role_collaborator(self, collaborator_id: int, data: UpdateCollaboratorsSchema, user_id: int) -> Collaborators:
        collaborator = await self.repository.get_by_id(collaborator_id)
        if not collaborator:
            raise CollaboratorNotFound()

        await self.project_authorization_service.require_project_owner(user_id, collaborator.id_project)

        for key, value in data.model_dump().items():
            setattr(collaborator, key, value)

        await self.repository.update(collaborator)

    async def get_collaborator_by_user_id_and_project_id(self, user_id: int, project_id: int) -> Collaborators | None:
        return await self.repository.get_collaborator_by_user_id_and_project_id(user_id, project_id)
