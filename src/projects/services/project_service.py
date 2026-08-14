from collaborators.interfaces import ICollaboratorService
from ..interfaces import IProjectService, IProjectAuthorizationService

from ..exceptions.project_exception import (
    ProjectAlreadyHasStatus,
    ProjectInsufficientPrivileges,
    ProjectNotFoundError,
)
from ..models.project import Project
from ..repositories.project_repository import ProjectRepository
from ..schemas.project_schema import (
    ListProjectDetail,
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
        project_authorization_service: IProjectAuthorizationService
    ):
        self.project_repo = project_repo
        self.collaborator_service = collaborator_service
        self.project_authorization_service = project_authorization_service

    async def get_project_by_id(self, id: int) -> Project:
        return await self._get_project_by_id_or_raise(id)

    async def _get_project_by_id_or_raise(self, id: int) -> Project:
        project = await self.project_repo.get_project_by_id(id)
        if not project:
            raise ProjectNotFoundError("Project not found")
        return project

    async def create_project(self, data: RegisterProjectInputSchema, user_id: int):
        project_to_created = ProjectCreateSchema(
            **data.model_dump(),
            owner_id=user_id
        )

        project_entity = Project(**project_to_created.model_dump())
        project_created: Project = await self.project_repo.create(project_entity)

        # Ownership is recorded by project.owner_id above. The collaborator row only
        # records membership; its role says what the person does on the project, and
        # the creator has not declared that yet.
        await self.collaborator_service.add_member_to_project(user_id, project_created.id, None)

    async def detail_project_by_id(self, id: int) -> ProjectDetail:
        project: Project = await self._get_project_by_id_or_raise(id)
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

        for field, value in update_fields.items():
            setattr(project, field, value)

        await self.project_repo.update(project)

    async def delete_project(self, id: int, user_id: int, data: dict):
        project: Project = await self.project_authorization_service.require_project_owner(user_id, id)

        if project.status == "CANCELLED":
            raise ProjectAlreadyHasStatus()

        for field, value in data.items():
            setattr(project, field, value)

        await self.project_repo.update(project)

    async def get_all_project(self, per_page: int, page: int) -> ListProjectDetail:
        projects_db, total = await self.project_repo.get_all_project(per_page, page)
        projects: list[ProjectDetail] = [ProjectDetail.model_validate(project) for project in projects_db]
        return ListProjectDetail(projects=projects, total=total)
