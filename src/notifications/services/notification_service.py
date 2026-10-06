import logging
from datetime import datetime, timezone

from ..exceptions import NotificationNotFound
from ..interfaces import INotificationService
from ..models.notification_model import Notification, NotificationType
from ..repositories.notification_repository import NotificationRepository
from ..schemas.notification_schema import ListNotificationOutputSchema, NotificationOutputSchema


logger = logging.getLogger(__name__)


class NotificationService(INotificationService):

    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    async def notify(self, user_id: int, actor_id: int, type: NotificationType, data: dict) -> None:
        # Nobody gets notified about their own actions.
        if user_id == actor_id:
            return
        # Best effort: a failed notification must not undo the action that triggered it.
        try:
            await self.notification_repository.create(
                Notification(user_id=user_id, type=type, data={**data, "actor_id": actor_id})
            )
        except Exception:
            logger.exception("Could not create %s notification for user %s", type, user_id)

    async def get_notifications(self, user_id: int, limit: int, offset: int) -> ListNotificationOutputSchema:
        notifications = await self.notification_repository.get_notifications_by_user_id(user_id, limit, offset)
        return ListNotificationOutputSchema(
            notifications=[NotificationOutputSchema.model_validate(notification) for notification in notifications],
            total=await self.notification_repository.count_by_user_id(user_id),
            unread=await self.notification_repository.count_by_user_id(user_id, unread_only=True),
            limit=limit,
            offset=offset,
        )

    async def mark_as_read(self, notification_id: int, user_id: int) -> None:
        notification = await self.notification_repository.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            raise NotificationNotFound()
        if notification.read_at is None:
            notification.read_at = datetime.now(timezone.utc)
            await self.notification_repository.update(notification)

    async def mark_all_as_read(self, user_id: int) -> None:
        await self.notification_repository.mark_all_as_read(user_id)
