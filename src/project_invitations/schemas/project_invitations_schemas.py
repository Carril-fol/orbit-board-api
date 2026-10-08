from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..models.project_invitation_model import InvitationStatus


class CreateProjectInvitation(BaseModel):
    """
    Schema for creating a project invitation.
    """
    id_project: int = Field(gt=0, description="The unique identifier of the project.", examples=[1])
    invitee_email: EmailStr = Field(..., description="Email address of the registered user being invited.", examples=["jane.doe@example.com"])
    role: str = Field(min_length=1, max_length=100, description="The role assigned to the user if they accept the invitation.", examples=["MEMBER"])

    @field_validator("role", mode="before")
    @classmethod
    def convert_to_uppercase(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value


class RespondInvitationInput(BaseModel):
    """
    Schema for responding to a project invitation.
    """
    id_invitation: int = Field(..., description="The unique identifier of the invitation.", examples=[50])
    accept: bool = Field(..., description="True to accept the invitation, False to reject it.", examples=[True])


class CreateInvitationOutput(BaseModel):
    """
    Schema returned after a successful project invitation creation.
    """
    msg: str = Field(..., description="Message confirming the invitation creation.", examples=["Invitation sent successfully"])
    token: str = Field(..., description="Secure token used to identify the invitation in the response URL.", examples=["abc123xyz789"])
    accept_url: str = Field(..., description="URL to accept the invitation.", examples=["https://api.example.com/invitations/accept?token=abc123xyz789"])
    reject_url: str = Field(..., description="URL to reject the invitation.", examples=["https://api.example.com/invitations/reject?token=abc123xyz789"])


class ReceivedInvitationSchema(BaseModel):
    """
    Schema for an invitation addressed to the authenticated user.
    """
    id: int = Field(..., description="Unique identifier of the invitation.", examples=[50])
    id_project: int = Field(..., description="The project the user is being invited to.", examples=[1])
    id_inviter: int = Field(..., description="The user who sent the invitation.", examples=[7])
    role: str = Field(..., description="The role the user gets if they accept.", examples=["MEMBER"])
    status: InvitationStatus = Field(..., description="The current status of the invitation.", examples=[InvitationStatus.PENDING])
    created_at: datetime = Field(..., description="When the invitation was sent.")
    token: str = Field(
        ...,
        description=(
            "Token that identifies this invitation. Answer it with "
            "`POST /invitations/api/v1/{token}/accept` or `/reject`."
        ),
        examples=["abc123xyz789"],
    )

    model_config = ConfigDict(from_attributes=True)


class ListReceivedInvitationSchema(BaseModel):
    """
    Schema for returning the invitations addressed to the authenticated user.
    """
    invitations: list[ReceivedInvitationSchema] = Field(..., description="Pending invitations for the user.")


class ProjectInvitationOutput(BaseModel):
    """
    Schema returned after a project invitation operation.
    """
    msg: str = Field(..., description="Message describing the result of the project invitation operation.", examples=["Invitation responded to successfully"])
