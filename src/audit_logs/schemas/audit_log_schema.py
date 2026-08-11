from typing import Optional, Any
from pydantic import BaseModel, Field


class AuditLogOutputSchema(BaseModel):
    """
    Schema for audit log entries tracking changes to entities.
    """
    id: int = Field(..., description="Unique identifier of the audit log entry.", examples=[1])
    user_id: int = Field(..., description="ID of the user who performed the action.", examples=[10])
    action: str = Field(..., description="Description of the action performed.", examples=["task_status_update"])
    entity_type: str = Field(..., description="Type of the entity affected.", examples=["Task"])
    entity_id: int = Field(..., description="ID of the affected entity.", examples=[100])

    old_value: Optional[dict[str, Any]] = Field(
        None,
        description="The state of the entity before the change. Null if it's a creation event.",
        examples=[{"status": "TO DO"}]
    )
    new_value: Optional[dict[str, Any]] = Field(
        None,
        description="The state of the entity after the change. Null if it's a deletion event.",
        examples=[{"status": "IN PROGRESS"}]
    )

    model_config = {
        "from_attributes": True
    }


class ListAuditLogOutputSchema(BaseModel):
    """
    Schema for returning a list of audit log entries.
    """
    logs: list[AuditLogOutputSchema] = Field(..., description="List of audit log entries for a specific entity.")
