from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from shared.database.base_repository import BaseRepository
from ..models.project import Project


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_project_by_id(self, id: int) -> Project | None:
        stmt = select(Project).where(Project.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_project(self, per_page: int, page: int) -> tuple[list[Project], int]:
        count_stmt = select(func.count()).select_from(self.model)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        stmt = select(self.model).offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(stmt)
        projects = result.scalars().all()

        return projects, total