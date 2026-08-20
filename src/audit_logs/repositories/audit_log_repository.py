from sqlalchemy import desc, func, select

from shared.database.base_repository import BaseRepository
from ..models.audit_log_model import AuditLog


class AuditLogRepository(BaseRepository[AuditLog]):

    def __init__(self, db):
        super().__init__(AuditLog, db)

    async def get_by_project(self, project_id: int, limit: int, offset: int):
        stmt = (
            select(AuditLog)
            .where(AuditLog.project_id == project_id)
            .order_by(desc(AuditLog.id))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_by_project(self, project_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.project_id == project_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
