from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class ProjectVisibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class RegisterProjectInputSchema(BaseModel):
    """
    Schema for registering a new project.
    """
    name: str = Field(
        min_length=3,
        max_length=100,
        description="The name of the project.",
        examples=["Project Alpha"]
    )
    status: ProjectStatus = Field(
        ...,
        description="The initial status of the project.",
        examples=[ProjectStatus.PLANNING]
    )
    description: str = Field(
        min_length=10,
        max_length=500,
        description="A detailed description of the project goals and scope.",
        examples=["Development of a new project management API."]
    )
    max_collaborators: int = Field(
        gt=0,
        description="The maximum number of collaborators allowed in the project.",
        examples=[10]
    )
    visibility: ProjectVisibility = Field(
        ProjectVisibility.PRIVATE,
        description=(
            "PRIVATE keeps the project readable only by its members. PUBLIC lists it on "
            "the open board, where any signed-in user can read it and ask to join."
        ),
        examples=[ProjectVisibility.PUBLIC]
    )
    
    @field_validator("visibility", mode="before")
    @classmethod
    def convert_to_uppercase(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value
    
class RegisterProjectOutputSchema(BaseModel):
    """
    Schema returned after a successful project registration.
    """
    msg: str = Field(..., description="Message confirming project creation.", examples=["Project created successfully"])


class UpdateProjectInputSchema(BaseModel):
    """
    Schema for updating project details.
    """
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Updated name of the project.", examples=["Project Beta"])
    status: Optional[ProjectStatus] = Field(None, description="Updated status of the project.", examples=[ProjectStatus.ACTIVE])
    description: Optional[str] = Field(None, min_length=10, max_length=500, description="Updated description of the project.", examples=["Updated goals for the project."])
    max_collaborators: Optional[int] = Field(None, description="Updated maximum number of collaborators.", examples=[15], gt=0)
    visibility: Optional[ProjectVisibility] = Field(None, description="Publish the project or take it back off the open board.", examples=[ProjectVisibility.PUBLIC])


class UpdateProjectOutputSchema(BaseModel):
    """
    Schema returned after a successful project update.
    """
    msg: str = Field(..., description="Message confirming project update.", examples=["Project updated successfully"])


class DeleteProjectOutputSchema(BaseModel):
    """
    Schema returned after a successful project deletion.
    """
    msg: str = Field(..., description="Message confirming project deletion.", examples=["Project deleted successfully"])


class ProjectCreateSchema(BaseModel):
    """
    Internal schema used to create a project record in the database.
    """
    name: str = Field(..., description="The name of the project.")
    status: str = Field(..., description="The status of the project.")
    description: str = Field(min_length=10, max_length=500, description="The description of the project.")
    max_collaborators: int = Field(gt=0, description="The maximum number of collaborators.")
    visibility: ProjectVisibility = Field(ProjectVisibility.PRIVATE, description="Whether the project is listed on the open board.")
    owner_id: int = Field(..., description="The ID of the user who owns the project.", examples=[1])

    @field_validator("status", mode="before")
    @classmethod
    def convert_to_uppercase(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value


class ProjectUpdateSchema(BaseModel):
    """
    Internal schema used to update a project record in the database.
    """
    name: Optional[str] = Field(None, description="The updated name of the project.")
    status: Optional[ProjectStatus] = Field(None, description="The updated status of the project.")
    description: Optional[str] = Field(None, description="The updated description of the project.")
    max_collaborators: Optional[int] = Field(None, description="The updated maximum number of collaborators.")
    visibility: Optional[ProjectVisibility] = Field(None, description="The updated visibility of the project.")
    owner_id: int = Field(..., description="The ID of the user who owns the project.", examples=[1])

    @field_validator("status", mode="before")
    @classmethod
    def convert_to_uppercase(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value


class ProjectDetail(BaseModel):
    """
    Schema for detailed project information.
    """
    id: int = Field(..., description="Unique identifier of the project.", examples=[1])
    name: str = Field(..., description="The name of the project.", examples=["Project Alpha"])
    status: str = Field(..., description="The current status of the project.", examples=["ACTIVE"])
    description: str = Field(..., description="The description of the project.", examples=["Development of a new API."])
    max_collaborators: int = Field(..., description="The maximum number of collaborators allowed.", examples=[10])
    visibility: str = Field(..., description="Whether the project is listed on the open board.", examples=["PUBLIC"])
    owner_id: int = Field(..., description="The ID of the project owner.", examples=[1])

    model_config = ConfigDict(from_attributes=True)


class ListProjectDetail(BaseModel):
    """
    Schema for returning a list of projects with pagination metadata.
    """
    projects: list[ProjectDetail] = Field(..., description="List of project details.")
    total: int = Field(..., description="Total number of projects found.", examples=[100])
