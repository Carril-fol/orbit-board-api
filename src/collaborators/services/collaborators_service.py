from projects.interfaces import IProjectAuthorizationService
from audit_logs.interfaces import IAuditLogService
from notifications.interfaces import INotificationService
from notifications.models.notification_model import NotificationType

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
        audit_log_service: IAuditLogService,
        project_authorization_service: IProjectAuthorizationService,
        notification_service: INotificationService,
    ):
        self.repository = repository
        self.audit_log_service = audit_log_service
        self.project_authorization_service = project_authorization_service
        self.notification_service = notification_service

    async def count_project_collaborators(self, project_id: int) -> int:
        return await self.repository.count_collaborators_from_project(project_id)

    async def require_project_member(self, user_id: int, project_id: int) -> Collaborators:
        collaborator = await self.repository.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if not collaborator:
            raise CollaboratorNotAuthorized()
        return collaborator

    async def add_member_to_project(self, id_user: int, id_project: int, role: str, actor_id: int) -> Collaborators:
        already_member = await self.repository.get_collaborator_by_user_id_and_project_id(id_user, id_project)
        if already_member:
            raise CollaboratorAlreadyExists()

        collaborators: int = await self.count_project_collaborators(id_project)
        await self.project_authorization_service.require_capacity_for(id_project, collaborators)

        data = RegisterCollaboratorsInputSchema(role=role, id_user=id_user, id_project=id_project).model_dump()
        collaborator_entity = Collaborators(**data)
        collaborator_created = await self.repository.create(collaborator_entity)

        await self.audit_log_service.record_event(
            user_id=actor_id,
            project_id=id_project,
            entity_type="Collaborator",
            entity_id=collaborator_created.id,
            action="add_member_to_project",
            data=collaborator_created.to_dict(),
        )

    async def get_collaborators(self, id_project: int, user_id: int) -> ListDetailCollaboratorsSchema:
        collaborators_raw = await self.repository.get_collaborators_from_project(id_project)

        user_ids: list[int] = [collaborator.id_user for collaborator in collaborators_raw]

        if user_id not in user_ids:
            raise CollaboratorNotAuthorized()

        collaborators_list: list[DetailCollaboratorsSchema] = [DetailCollaboratorsSchema.model_validate(collaborator) for collaborator in collaborators_raw]
        return ListDetailCollaboratorsSchema(collaborators=collaborators_list)

    async def remove_collaborator(self, collaborator_id: int, user_id: int):
        collaborator: Collaborators = await self.repository.get_by_id(collaborator_id)
        if not collaborator:
            raise CollaboratorNotFound()

        await self.project_authorization_service.require_project_owner(user_id, collaborator.id_project)

        removed_state = collaborator.to_dict()

        await self.repository.delete(collaborator_id)

        await self.audit_log_service.record_event(
            user_id=user_id,
            project_id=removed_state["id_project"],
            entity_type="Collaborator",
            entity_id=collaborator_id,
            action="remove_collaborator",
            data=removed_state,
        )
        await self.notification_service.notify(
            user_id=removed_state["id_user"],
            actor_id=user_id,
            type=NotificationType.REMOVED_FROM_PROJECT,
            data={"project_id": removed_state["id_project"]},
        )

    async def change_role_collaborator(self, collaborator_id: int, data: UpdateCollaboratorsSchema, user_id: int) -> Collaborators:
        collaborator = await self.repository.get_by_id(collaborator_id)
        if not collaborator:
            raise CollaboratorNotFound()

        await self.project_authorization_service.require_project_owner(user_id, collaborator.id_project)

        old_state = collaborator.to_dict()

        for key, value in data.model_dump().items():
            setattr(collaborator, key, value)

        new_state = collaborator.to_dict()

        await self.repository.update(collaborator)

        await self.audit_log_service.record_diff(
            user_id=user_id,
            project_id=collaborator.id_project,
            entity_type="Collaborator",
            entity_id=collaborator.id,
            action="change_role_collaborator",
            old_state=old_state,
            new_state=new_state,
        )
        if old_state["role"] != new_state["role"]:
            await self.notification_service.notify(
                user_id=collaborator.id_user,
                actor_id=user_id,
                type=NotificationType.ROLE_CHANGED,
                data={"project_id": collaborator.id_project, "role": collaborator.role},
            )

    async def get_project_ids_for_user(self, user_id: int) -> list[int]:
        collaborators = await self.repository.get_collaborator_by_user_id(user_id)
        return [collaborator.id_project for collaborator in collaborators]

    async def get_collaborator_by_user_id_and_project_id(self, user_id: int, project_id: int) -> Collaborators | None:
        return await self.repository.get_collaborator_by_user_id_and_project_id(user_id, project_id)
