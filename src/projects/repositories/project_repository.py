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

    async def get_projects_by_ids(self, project_ids: list[int], per_page: int, page: int) -> tuple[list[Project], int]:
        if not project_ids:
            return [], 0

        filters = (Project.id.in_(project_ids), Project.status != "CANCELED")

        count_stmt = select(func.count()).select_from(self.model).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar()

        stmt = (
            select(self.model)
            .where(*filters)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(stmt)

        return result.scalars().all(), total

    async def get_all_project(self, per_page: int, page: int) -> tuple[list[Project], int]:
        filters = (Project.status != "CANCELED", Project.visibility == "PUBLIC")

        count_stmt = select(func.count()).select_from(self.model).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar()

        stmt = (
            select(self.model)
            .where(*filters)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(stmt)

        return result.scalars().all(), total
    
    async def get_project_by_name(self, name: str) -> Project:
        stmt = select(Project).where(Project.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()