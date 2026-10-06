from collaborators.interfaces import ICollaboratorService
from audit_logs.interfaces import IAuditLogService
from ..interfaces import IProjectService, IProjectAuthorizationService

from ..exceptions import (
    ProjectAlreadyHasStatus,
    ProjectNotFoundError,
    ProjectInsufficientPrivileges
)
from ..models.project import Project
from ..repositories.project_repository import ProjectRepository
from ..schemas.project_schema import (
    ListProjectDetail,
    ProjectStatus,
    ProjectVisibility,
    ProjectCreateSchema,
    ProjectDetail,
    ProjectUpdateSchema,
    RegisterProjectInputSchema,
    UpdateProjectInputSchema,
)


class ProjectService(IProjectService):
    def __init__(
        self, project_repo: ProjectRepository,
        collaborator_service: ICollaboratorService,
        audit_log_service: IAuditLogService,
        project_authorization_service: IProjectAuthorizationService
    ):
        self.project_repo = project_repo
        self.collaborator_service = collaborator_service
        self.audit_log_service = audit_log_service
        self.project_authorization_service = project_authorization_service

    async def get_project_by_id(self, id: int) -> Project:
        return await self._get_project_by_id_or_raise(id)

    async def _get_project_by_id_or_raise(self, id: int) -> Project:
        project = await self.project_repo.get_project_by_id(id)
        if not project:
            raise ProjectNotFoundError()
        return project

    async def _require_reader_of(self, project: Project, user_id: int) -> None:
        if project.owner_id == user_id:
            return

        collaborator = await self.collaborator_service.get_collaborator_by_user_id_and_project_id(
            user_id, project.id
        )
        if not collaborator:
            raise ProjectInsufficientPrivileges()

    async def create_project(self, data: RegisterProjectInputSchema, user_id: int):
        project_to_created = ProjectCreateSchema(
            **data.model_dump(),
            owner_id=user_id
        )

        project_entity = Project(**project_to_created.model_dump())
        project_created: Project = await self.project_repo.create(project_entity)
        
        await self.audit_log_service.record_event(
            user_id=user_id,
            project_id=project_created.id,
            entity_type="Project",
            entity_id=project_created.id,
            action="create_project",
            data=project_created.to_dict(),
        )

        await self.collaborator_service.add_member_to_project(user_id, project_created.id, None, user_id)

    async def detail_project_by_id(self, id: int, user_id: int) -> ProjectDetail:
        project: Project = await self._get_project_by_id_or_raise(id)

        if project.visibility != ProjectVisibility.PUBLIC:
            await self._require_reader_of(project, user_id)

        return ProjectDetail.model_validate(project)

    async def update_project(self, id: int, data: UpdateProjectInputSchema, user_id: int):
        project: Project = await self.project_authorization_service.require_project_owner(user_id, id)

        project_update = ProjectUpdateSchema(
            **data.model_dump(exclude_unset=True),
            owner_id=user_id
        )

        update_fields = project_update.model_dump(
            exclude_unset=True,
            exclude={"owner_id"}
        )

        old_state = project.to_dict()

        for field, value in update_fields.items():
            setattr(project, field, value)

        new_state = project.to_dict()

        await self.project_repo.update(project)

        await self.audit_log_service.record_diff(
            user_id=user_id,
            project_id=project.id,
            entity_type="Project",
            entity_id=project.id,
            action="update_project",
            old_state=old_state,
            new_state=new_state,
        )

    async def delete_project(self, id: int, user_id: int):
        project: Project = await self.project_authorization_service.require_project_owner(user_id, id)

        if project.status == ProjectStatus.CANCELED:
            raise ProjectAlreadyHasStatus()

        project.status = ProjectStatus.CANCELED.value

        await self.project_repo.update(project)

        await self.audit_log_service.record_event(
            user_id=user_id,
            project_id=project.id,
            entity_type="Project",
            entity_id=project.id,
            action="delete_project",
            data=project.to_dict(),
        )

    async def get_projects_for_user(
        self, user_id: int, limit: int, offset: int
    ) -> ListProjectDetail:
        project_ids = await self.collaborator_service.get_project_ids_for_user(user_id)
        projects_db, total = await self.project_repo.get_projects_by_ids(project_ids, limit, offset)
        projects: list[ProjectDetail] = [ProjectDetail.model_validate(project) for project in projects_db]
        return ListProjectDetail(projects=projects, total=total, limit=limit, offset=offset)

    async def get_all_project(self, limit: int, offset: int) -> ListProjectDetail:
        projects_db, total = await self.project_repo.get_all_project(limit, offset)
        projects: list[ProjectDetail] = [ProjectDetail.model_validate(project) for project in projects_db]
        return ListProjectDetail(projects=projects, total=total, limit=limit, offset=offset)
