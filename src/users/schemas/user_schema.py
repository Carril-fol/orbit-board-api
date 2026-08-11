from pydantic import BaseModel, Field

class UserResponse(BaseModel):
    """
    Schema for returning user profile information.
    """
    id: int = Field(..., description="Unique identifier of the user.", examples=[1])
    first_name: str = Field(..., description="User's first name.", examples=["John"])
    last_name: str = Field(..., description="User's last name.", examples=["Doe"])
    username: str = Field(..., description="Unique username of the user.", examples=["johndoe123"])
    bio: str = Field(..., description="User's short biography or description.", examples=["Software Engineer and tech enthusiast"])
    email: str = Field(..., description="User's email address.", examples=["john.doe@example.com"])

    class Config:
        from_attributes: True