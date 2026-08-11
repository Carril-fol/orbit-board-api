from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CommentBaseSchema(BaseModel):
    """
    Base schema for comment-related data.
    """
    content: str = Field(..., description="The content of the comment.", examples=["This is a helpful comment on the task."])
    task_id: int = Field(..., description="The unique identifier of the task associated with the comment.", examples=[100])
    user_id: int = Field(..., description="The unique identifier of the user who created the comment.", examples=[10])


class RegisterCommentInputSchema(BaseModel):
    """
    Schema for submitting a new comment.
    """
    content: str = Field(..., description="The content of the comment.", examples=["I've started working on this task."])


class CreateCommentSchema(CommentBaseSchema):
    """
    Internal schema used to create a comment record in the database.
    """
    pass


class DetailCommentOutputSchema(CommentBaseSchema):
    """
    Schema for detailed comment information.
    """
    id: int = Field(..., description="The unique identifier of the comment.", examples=[1])
    content: str = Field(..., description="The content of the comment.", examples=["This is a helpful comment on the task."])
    created_at: datetime = Field(..., description="The UTC timestamp when the comment was created.")
    updated_at: datetime = Field(..., description="The UTC timestamp when the comment was last updated.")

    model_config = ConfigDict(from_attributes=True)


class ListDetailCommentOutputSchema(BaseModel):
    """
    Schema for returning a paginated list of comments.
    """
    comments: list[DetailCommentOutputSchema] = Field(..., description="List of comments.")
    total: int = Field(..., description="Total number of comments found.", examples=[50])
    limit: int = Field(..., description="Number of comments returned per page.", examples=[10])
    offset: int = Field(..., description="The current offset for pagination.", examples=[0])


class UpdateCommentSchema(BaseModel):
    """
    Schema for updating the content of an existing comment.
    """
    content: str = Field(..., description="The updated content of the comment.", examples=["Updated comment content."])


class CommentOutputSchema(BaseModel):
    """
    Schema returned after a comment operation.
    """
    msg: str = Field(
        ...,
        description="A message indicating the result of the operation.",
        examples=["Comment created successfully"]
    )
