from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NotificationOutputSchema(BaseModel):
    """
    Schema for a single notification.
    """
    id: int = Field(..., description="The unique identifier of the notification.", examples=[1])
    type: str = Field(..., description="The kind of event that triggered the notification.", examples=["invitation_received"])
    data: dict = Field(..., description="Event payload; its keys depend on the notification type.", examples=[{"invitation_id": 3, "project_id": 7}])
    read_at: datetime | None = Field(None, description="The UTC timestamp when the notification was read, or null if unread.")
    created_at: datetime = Field(..., description="The UTC timestamp when the notification was created.")

    model_config = ConfigDict(from_attributes=True)


class ListNotificationOutputSchema(BaseModel):
    """
    Schema for returning a page of notifications, newest first.
    """
    notifications: list[NotificationOutputSchema] = Field(..., description="Notifications of the current user.")
    total: int = Field(..., description="Total number of notifications of the user.", examples=[42])
    unread: int = Field(..., description="Number of unread notifications of the user.", examples=[3])
    limit: int = Field(..., description="Maximum number of notifications returned.", examples=[20])
    offset: int = Field(..., description="Number of notifications skipped.", examples=[0])


class NotificationMessageSchema(BaseModel):
    """
    Schema for a confirmation message.
    """
    msg: str = Field(..., description="Confirmation message.", examples=["Notification marked as read"])
