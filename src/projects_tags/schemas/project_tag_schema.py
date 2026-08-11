from pydantic import BaseModel, Field, field_validator

class RegisterProjectTagInputSchema(BaseModel):
    """
    Schema for adding a tag to a project.
    """
    tag: str = Field(
        min_length=3,
        max_length=100,
        description="The tag name to associate with the project.",
        examples=["URGENT"]
    )


class ProjectTagOutputSchema(BaseModel):
    """
    Schema returned after a successful project tag operation.
    """
    msg: str = Field(
        ...,
        description="Message describing the result of the project tag operation.",
        examples=["Tag added successfully"]
    )


class CreateProjectTag(BaseModel):
    """
    Internal schema used to create a project tag in the database.
    """
    id_project: int = Field(..., description="The unique identifier of the project.", examples=[1])
    tag: str = Field(..., description="The tag name.", examples=["URGENT"])

    @field_validator("tag", mode='before')
    @classmethod
    def convert_to_uppercase(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value
