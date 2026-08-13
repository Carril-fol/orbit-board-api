import string
from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


def password_strength_check(value: str) -> str:
    if not any(char in string.punctuation for char in value):
        raise ValueError("La contraseña debe contener al menos un carácter especial")
    return value


class RegisterInputSchema(BaseModel):
    """
    Schema for registering a new user.
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
        description="Unique username used to identify the user.",
        examples=["John123"],
    )
    email: EmailStr = Field(
        ...,
        description="User's email address.",
        examples=["john.marston@gmail.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=15,
        description=(
            "User's password. Must be between 8 and 15 characters "
            "and contain at least one special character."
        ),
        examples=["Supersecure123-"],
    )

    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=15,
        description="Confirmation of the user's password.",
        examples=["Supersecure123-"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        return password_strength_check(value)

    @model_validator(mode="after")
    def validate_confirm_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Password not match")
        return self


class LoginInputSchema(BaseModel):
    """
    Schema for authenticating an existing user.
    """
    email: EmailStr = Field(
        ...,
        description="Email address associated with the user account.",
        examples=["example@gmail.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=15,
        description="User's password.",
        examples=["Supersecure123-"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        return password_strength_check(value)


class LoginOutputSchema(BaseModel):
    """
    Schema containing the authentication tokens returned after login.
    """
    access_token: str = Field(
        ...,
        description="Short-lived JWT access token used to authenticate API requests.",
        examples=["eyJhbGciOiJIUzI1NiIs..."],
    )
    refresh_token: str = Field(
        ...,
        description="Long-lived JWT refresh token used to obtain a new access token.",
        examples=["eyJhbGciOiJIUzI1NiIs..."],
    )


class AuthOutputSchema(BaseModel):
    """
    Schema returned after a successful authentication operation.
    """
    
    msg: str = Field(
        ...,
        description="Message describing the result of the authentication operation.",
        examples=["Authentication successful"],
    )