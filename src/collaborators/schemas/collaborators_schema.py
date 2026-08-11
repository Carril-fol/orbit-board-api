from pydantic import BaseModel, field_validator, Field

from users.schemas.user_schema import UserResponse


class RegisterCollaboratorsInputSchema(BaseModel):
    """
    Schema for registering a user as a collaborator in a project.
    """
    role: str = Field(
        ...,
        description="Role assigned to the user within the project.",
        examples=["MEMBER"],
    )
    id_project: int = Field(
        ...,
        description="Unique identifier of the project.",
        examples=[1],
    )
    id_user: int = Field(
        ...,
        description="Unique identifier of the user to be added as a collaborator.",
        examples=[10],
    )


class CreateCollaboratorsSchema(BaseModel):
    """
    Internal schema used to create a collaborator record in the database.
    """
    role: str = Field(
        ...,
        description="Role assigned to the user within the project.",
        examples=["MEMBER"],
    )
    id_project: int = Field(
        ...,
        description="Unique identifier of the project.",
        examples=[1],
    )
    id_user: int = Field(
        ...,
        description="Unique identifier of the user associated with the project.",
        examples=[10],
    )

    @field_validator("role", mode="before")
    @classmethod
    def convert_to_uppercase(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value


class DetailCollaboratorsSchema(BaseModel):
    """
    Schema for detailed collaborator information.
    """
    role: str = Field(
        ...,
        description="Role assigned to the collaborator within the project.",
        examples=["MEMBER"],
    )
    user: UserResponse = Field(
        ...,
        description="User information associated with the collaborator.",
    )

    class Config:
        from_attributes = True


class ListDetailCollaboratorsSchema(BaseModel):
    """
    Schema for returning a list of collaborators in a project.
    """
    collaborators: list[DetailCollaboratorsSchema] = Field(
        ...,
        description="List of collaborators associated with the project.",
    )


class UpdateCollaboratorsSchema(BaseModel):
    """
    Schema for updating a collaborator's role.
    """
    role: str = Field(
        ...,
        description="New role assigned to the collaborator.",
        examples=["ADMIN"],
    )

    @field_validator("role", mode="before")
    @classmethod
    def convert_to_uppercase(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value


class CollaboratorsOutputSchema(BaseModel):
    """
    Schema returned after a collaborator operation.
    """
    msg: str = Field(
        ...,
        description="Message describing the result of the collaborator operation.",
        examples=["Collaborator created successfully"],
    )
