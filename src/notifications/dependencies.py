from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_async_db

from .interfaces import INotificationService
from .repositories.notification_repository import NotificationRepository
from .services.notification_service import NotificationService


def get_notifications_repository(db: AsyncSession = Depends(get_async_db, scope="function")) -> NotificationRepository:
    return NotificationRepository(db)


def get_notifications_service(
    repo: NotificationRepository = Depends(get_notifications_repository),
) -> INotificationService:
    return NotificationService(repo)
