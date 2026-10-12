from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import CurrentUserId
from shared.extensions import limiter, READ_LIMIT, WRITE_LIMIT
from shared.pagination import Pagination

from ..interfaces import INotificationService
from ..dependencies import get_notifications_service
from ..schemas.notification_schema import (
    ListNotificationOutputSchema,
    NotificationMessageSchema,
)

router = APIRouter(prefix="/notifications/api/v1", tags=["Notifications"])


@router.get(
    "/",
    response_model=ListNotificationOutputSchema,
    status_code=200,
)
@limiter.limit(READ_LIMIT)
async def get_notifications(
    user_id: CurrentUserId,
    request: Request,
    page: Pagination,
    service: INotificationService = Depends(get_notifications_service),
):
    return await service.get_notifications(user_id, page.limit, page.offset)


@router.patch(
    "/read-all",
    response_model=NotificationMessageSchema,
    status_code=200,
)
@limiter.limit(WRITE_LIMIT)
async def mark_all_notifications_as_read(
    user_id: CurrentUserId,
    request: Request,
    service: INotificationService = Depends(get_notifications_service),
):
    await service.mark_all_as_read(user_id)
    return NotificationMessageSchema(msg="All notifications marked as read")


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationMessageSchema,
    status_code=200,
)
@limiter.limit(WRITE_LIMIT)
async def mark_notification_as_read(
    user_id: CurrentUserId,
    request: Request,
    notification_id: int,
    service: INotificationService = Depends(get_notifications_service),
):
    await service.mark_as_read(notification_id, user_id)
    return NotificationMessageSchema(msg="Notification marked as read")
