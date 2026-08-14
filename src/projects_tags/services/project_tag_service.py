from projects.interfaces import IProjectAuthorizationService

from ..models.project_tag_model import ProjectTag
from ..repositories.project_tag_repository import ProjectTagRepository
from ..exceptions import ProjectTagNotFound
from ..schemas.project_tag_schema import CreateProjectTag, RegisterProjectTagInputSchema
from ..interfaces import IProjectTagService


class ProjectTagService(IProjectTagService):
    def __init__(
        self,
        repo: ProjectTagRepository,
        project_authorization_service: IProjectAuthorizationService
    ):
        self.repo = repo
        self.project_authorization_service = project_authorization_service

    async def _get_project_tag_or_raise(self, id_tag: int) -> ProjectTag:
        project_tag = await self.repo.get_project_tag_by_id(id_tag)
        if not project_tag:
            raise ProjectTagNotFound()

        return project_tag

    async def create_project_tag(self, id_project: int, data: RegisterProjectTagInputSchema, user_id: int) -> None:
        await self.project_authorization_service.require_project_owner(user_id, id_project)

        project_tag_data = CreateProjectTag(tag=data.tag, id_project=id_project)
        project_to_create = ProjectTag(**project_tag_data.model_dump())
        await self.repo.create(project_to_create)

    async def delete_tag_from_project(self, id_tag: int, user_id: int) -> None:
        project_tag = await self._get_project_tag_or_raise(id_tag)

        await self.project_authorization_service.require_project_owner(user_id, project_tag.id_project)

        await self.repo.delete(project_tag)
