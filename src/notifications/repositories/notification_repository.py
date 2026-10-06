from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.base_repository import BaseRepository
from ..models.notification_model import Notification


class NotificationRepository(BaseRepository[Notification]):

    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def create(self, entity: Notification) -> Notification:
        # A savepoint, so a failed insert rolls back only the notification and
        # leaves the request's transaction usable.
        async with self.db.begin_nested():
            return await super().create(entity)

    async def get_notifications_by_user_id(self, user_id: int, limit: int, offset: int):
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_by_user_id(self, user_id: int, unread_only: bool = False) -> int:
        stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.read_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def mark_all_as_read(self, user_id: int) -> None:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
            .values(read_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
