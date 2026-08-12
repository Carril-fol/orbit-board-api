from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.base_repository import BaseRepository
from ..models.project_tag_model import ProjectTag


class ProjectTagRepository(BaseRepository[ProjectTag]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectTag, db)

    async def get_project_tag_by_id(self, id: int) -> ProjectTag | None:
        stmt = select(ProjectTag).where(ProjectTag.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_logic(self, project_tag: ProjectTag) -> ProjectTag:
        return await self.update(project_tag)
