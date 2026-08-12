from projects.repositories.project_repository import ProjectRepository
from projects.models.project import Project

from ..models.project_tag_model import ProjectTag
from ..repositories.project_tag_repository import ProjectTagRepository
from ..exceptions import ProjectNotFound, ProjectTagNotFound, ProjectTagNotAllowed
from ..schemas.project_tag_schema import CreateProjectTag, RegisterProjectTagInputSchema


class ProjectTagService:
    def __init__(
        self, 
        repo: ProjectTagRepository, 
        project_repo: ProjectRepository
    ):
        self.repo = repo
        self.project_repo = project_repo

    def _ensure_is_owner(self, project: Project, user_id: int) -> None:
        if project.owner_id != int(user_id):
            raise ProjectTagNotAllowed()

    async def _get_project_tag_or_raise(self, id_tag: int) -> ProjectTag:
        project_tag = await self.repo.get_project_tag_by_id(id_tag)
        if not project_tag:
            raise ProjectTagNotFound()
        
        return project_tag

    async def _get_project_or_raise(self, project_id: int) -> Project :
        project = await self.project_repo.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFound()
        
        return project

    async def create_project_tag(self, id_project: int, data: RegisterProjectTagInputSchema, user_id: int) -> None:
        project = await self._get_project_or_raise(id_project)

        self._ensure_is_owner(project, user_id)

        project_tag_data = CreateProjectTag(tag=data.tag, id_project=id_project)
        project_to_create = ProjectTag(**project_tag_data.model_dump())
        await self.repo.create(project_to_create)

    async def delete_tag_from_project(self, id_tag: int, user_id: int) -> None:
        project_tag = await self._get_project_tag_or_raise(id_tag)

        project = await self._get_project_or_raise(project_tag.id_project)

        self._ensure_is_owner(project, user_id)
        await self.repo.delete(project_tag)
