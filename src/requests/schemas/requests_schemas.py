from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RegisterRequestsInputSchema(BaseModel):
    """
    Schema for submitting a project access request.
    """
    message: Optional[str] = Field(
        None,
        description="Optional message providing context or justification for the request.",
        examples=["I would like to contribute to the frontend development."]
    )
    role: str = Field(
        ...,
        description="The role the user is requesting within the project.",
        examples=["MEMBER"]
    )


class CreateRequestSchema(BaseModel):
    """
    Internal schema used to create an access request record in the database.
    """
    message: Optional[str] = Field(None, description="Optional message for the request.")
    role: str = Field(..., description="The requested role.")
    project_id: int = Field(..., description="The unique identifier of the project.", examples=[1])
    user_id: int = Field(..., description="The unique identifier of the user making the request.", examples=[10])
    status: RequestStatus = Field(
        default=RequestStatus.PENDING,
        description="The current status of the request.",
        examples=[RequestStatus.PENDING]
    )

    @field_validator("role")
    @classmethod
    def upper_value(cls, v):
        return v.upper()

    @field_validator("project_id", "user_id")
    @classmethod
    def validate_ids(cls, v):
        if not v:
            raise ValueError("project_id and user_id cannot be empty")
        return v


class UpdateRequestSchema(BaseModel):
    """
    Schema for updating the status of an access request.
    """
    status: RequestStatus = Field(
        ...,
        description="The new status to apply to the request.",
        examples=[RequestStatus.APPROVED]
    )


class DetailRequestSchema(BaseModel):
    """
    Schema for detailed access request information.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique identifier of the request.", examples=[1])
    message: Optional[str] = Field(None, description="The message associated with the request.", examples=["I want to help."])
    project_id: int = Field(..., description="The unique identifier of the project.", examples=[1])
    user_id: int = Field(..., description="The unique identifier of the user.", examples=[10])
    status: RequestStatus = Field(..., description="The current status of the request.", examples=[RequestStatus.PENDING])
    review_at: Optional[datetime] = Field(None, description="When the owner answered the request, or null while it is pending.")


class ListDetailRequestSchema(BaseModel):
    """
    Schema for returning a list of access requests.
    """
    requests: list[DetailRequestSchema] = Field(..., description="List of request details.")


class SentRequestSchema(BaseModel):
    """
    Schema for an access request submitted by the authenticated user.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique identifier of the request.", examples=[1])
    project_id: int = Field(..., description="The project the user asked to join.", examples=[1])
    role: str = Field(..., description="The role the user asked for.", examples=["MEMBER"])
    message: Optional[str] = Field(None, description="The message sent with the request.", examples=["I want to help."])
    status: RequestStatus = Field(..., description="The current status of the request.", examples=[RequestStatus.PENDING])
    created_at: datetime = Field(..., description="When the request was submitted.")
    review_at: Optional[datetime] = Field(None, description="When the owner answered the request, or null while it is pending.")


class ListSentRequestSchema(BaseModel):
    """
    Schema for returning the access requests submitted by the authenticated user.
    """
    requests: list[SentRequestSchema] = Field(..., description="Requests submitted by the user, newest first.")


class RequestOutputSchema(BaseModel):
    """
    Schema returned after a request operation.
    """
    msg: str = Field(
        ...,
        description="Message describing the result of the request operation.",
        examples=["Request submitted successfully"]
    )
