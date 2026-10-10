from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.base_repository import BaseRepository
from ..models.requests_model import Request


class RequestsRepository(BaseRepository[Request]):
    def __init__(self, db: AsyncSession):
        super().__init__(Request, db)

    async def get_request_by_id(self, request_id: int) -> Request | None:
        stmt = select(Request).where(Request.id == request_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_requests_by_project_id(self, project_id: int) -> list[Request]:
        stmt = select(Request).where(Request.project_id == project_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_requests_by_user_id(self, user_id: int) -> list[Request]:
        stmt = (
            select(Request)
            .where(Request.user_id == user_id)
            .order_by(Request.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_request_by_user_id_and_project_id(
        self, user_id: int, project_id: int
    ) -> Request | None:
        stmt = (
            select(Request)
            .where(
                Request.user_id == user_id,
                Request.project_id == project_id
            )
            .order_by(Request.id.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
