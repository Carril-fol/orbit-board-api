from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

class UserResponse(BaseModel):
    """
    Schema for returning user profile information.
    """
    id: int = Field(..., description="Unique identifier of the user.", examples=[1])
    first_name: str = Field(..., description="User's first name.", examples=["John"])
    last_name: str = Field(..., description="User's last name.", examples=["Doe"])
    username: str | None = Field(None, description="Unique username of the user.", examples=["johndoe123"])
    email: str = Field(..., description="User's email address.", examples=["john.doe@example.com"])
    
    model_config = ConfigDict(from_attributes=True)
        

class UserCreateSchema(BaseModel):
    """
    Schema used to create a new user in the database.
    """
    first_name: str = Field(
        ...,
        description="User's first name.",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        description="User's last name.",
        examples=["Marston"],
    )
    username: str = Field(
        ...,
        description="Unique username assigned to the user.",
        examples=["John123"],
    )
    email: EmailStr = Field(
        ...,
        description="User's email address.",
        examples=["john.marston@gmail.com"],
    )
    password: str = Field(
        ...,
        description="Hashed password stored for the user.",
        examples=["$argon2id$v=19$m=65536,t=3,p=4$..."],
    )
    date_created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp indicating when the user was created.",
    )
    date_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp indicating when the user was last updated.",
    )