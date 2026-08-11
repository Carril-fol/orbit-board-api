from pydantic import BaseModel, Field, field_validator


class ProjectInvitationBase(BaseModel):
    """
    Base schema for project invitations.
    """
    id_project: int = Field(gt=0, description="The unique identifier of the project.", examples=[1])
    id_invitee: int = Field(gt=0, description="The unique identifier of the user being invited.", examples=[10])
    role: str = Field(min_length=1, max_length=100, description="The role assigned to the user if they accept the invitation.", examples=["MEMBER"])


class CreateProjectInvitation(ProjectInvitationBase):
    """
    Schema for creating a project invitation.
    """
    pass

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


class ProjectInvitationOutput(BaseModel):
    """
    Schema returned after a project invitation operation.
    """
    msg: str = Field(..., description="Message describing the result of the project invitation operation.", examples=["Invitation responded to successfully"])
