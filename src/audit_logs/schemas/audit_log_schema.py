from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class AuditLogOutputSchema(BaseModel):
    """
    Schema for audit log entries tracking changes to entities.
    """
    id: int = Field(..., description="Unique identifier of the audit log entry.", examples=[1])
    user_id: int = Field(..., description="ID of the user who performed the action.", examples=[10])
    project_id: int = Field(..., description="ID of the project the action happened in.", examples=[1])
    action: str = Field(..., description="Description of the action performed.", examples=["task_status_update"])
    entity_type: str = Field(..., description="Type of the entity affected.", examples=["Task"])
    entity_id: int = Field(..., description="ID of the affected entity.", examples=[100])
    timestamp: datetime = Field(..., description="When the action was recorded.")

    old_value: dict[str, Any] = Field(
        ...,
        description="The state of the entity before the change. Empty for creation events.",
        examples=[{"status": "TO DO"}]
    )
    new_value: dict[str, Any] = Field(
        ...,
        description="The state of the entity after the change.",
        examples=[{"status": "IN PROGRESS"}]
    )

    model_config = {
        "from_attributes": True
    }


class ListAuditLogOutputSchema(BaseModel):
    """
    Schema for returning a page of audit log entries, newest first.
    """
    logs: list[AuditLogOutputSchema] = Field(..., description="Audit log entries for the project.")
    total: int = Field(..., description="Total number of entries recorded for the project.", examples=[120])
    limit: int = Field(..., description="Maximum number of entries returned.", examples=[50])
    offset: int = Field(..., description="Number of entries skipped.", examples=[0])
