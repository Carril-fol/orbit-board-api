from abc import ABC, abstractmethod

from .models.notification_model import NotificationType
from .schemas.notification_schema import ListNotificationOutputSchema


class INotificationService(ABC):
    @abstractmethod
    async def notify(self, user_id: int, actor_id: int, type: NotificationType, data: dict) -> None:
        pass

    @abstractmethod
    async def get_notifications(self, user_id: int, limit: int, offset: int) -> ListNotificationOutputSchema:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def mark_all_as_read(self, user_id: int) -> None:
        pass
