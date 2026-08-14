from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from ..models.task_model import TaskPriority, TaskStatus


class TaskBaseSchema(BaseModel):
    """
    Base schema for task-related data.
    """
    title: str = Field(..., description="The title of the task", examples=["Implement User Authentication"])
    description: Optional[str] = Field(None, description="Detailed description of the task requirements", examples=["Create JWT based auth system with refresh tokens"])
    status: TaskStatus = Field(..., description="The current state of the task (TO DO, IN PROGRESS, REVIEW, DONE)", examples=[TaskStatus.TO_DO])
    priority: TaskPriority = Field(..., description="Priority level of the task (LOW, MEDIUM, HIGH)", examples=[TaskPriority.MEDIUM])
    expiration_date: Optional[datetime] = Field(None, description="Optional deadline for the task completion")


class RegisterTaskInputSchema(TaskBaseSchema):
    """
    Schema for submitting a new task.
    """
    parent_id: Optional[int] = Field(None, description="The ID of the parent task if this is a subtask", examples=[10])


class CreateTaskInputSchema(TaskBaseSchema):
    """
    Internal schema used to create a task record in the database.
    """
    project_id: int = Field(..., description="The ID of the project this task belongs to", examples=[1])
    parent_id: Optional[int] = Field(None, description="The ID of the parent task for hierarchical structure", examples=[10])


class UpdateTaskInputSchema(BaseModel):
    """
    Schema for updating task details.
    """
    title: Optional[str] = Field(None, description="Updated title of the task", examples=["Implement User Authentication v2"])
    description: Optional[str] = Field(None, description="Updated description", examples=["Updated requirements..."])
    status: Optional[TaskStatus] = Field(None, description="New status of the task", examples=[TaskStatus.IN_PROGRESS])
    priority: Optional[TaskPriority] = Field(None, description="New priority level", examples=[TaskPriority.HIGH])
    expiration_date: Optional[datetime] = Field(None, description="New expiration date")
    parent_id: Optional[int] = Field(None, description="Change the parent task of this task", examples=[12])


class SubtaskOutputSchema(BaseModel):
    """
    Schema for a subtask nested inside a task.

    Deliberately non-recursive: subtasks are one level deep, so serializing a task
    never needs to load a deeper level of the tree.
    """
    id: int = Field(..., description="The unique identifier of the subtask", examples=[2])
    title: str = Field(..., description="The title of the subtask", examples=["Write the token refresh endpoint"])
    description: Optional[str] = Field(None, description="Detailed description of the subtask", examples=["Rotate the refresh token on every use..."])
    status: TaskStatus = Field(..., description="The current state of the subtask", examples=[TaskStatus.TO_DO])
    priority: TaskPriority = Field(..., description="Priority level of the subtask", examples=[TaskPriority.MEDIUM])
    expiration_date: Optional[datetime] = Field(None, description="Deadline for the subtask")
    project_id: int = Field(..., description="The ID of the project this subtask is associated with", examples=[1])
    parent_id: Optional[int] = Field(None, description="The ID of the parent task", examples=[10])
    deleted_at: Optional[datetime] = Field(None, description="Timestamp when the subtask was deleted.")

    class Config:
        from_attributes = True


class DetailTaskOutputSchema(BaseModel):
    """
    Schema for detailed task information.
    """
    id: int = Field(..., description="The unique identifier of the task", examples=[1])
    title: str = Field(..., description="The title of the task", examples=["Implement User Authentication"])
    description: Optional[str] = Field(None, description="Detailed description of the task", examples=["Create JWT based auth system..."])
    status: TaskStatus = Field(..., description="The current state of the task", examples=[TaskStatus.TO_DO])
    priority: TaskPriority = Field(..., description="Priority level of the task", examples=[TaskPriority.MEDIUM])
    expiration_date: Optional[datetime] = Field(None, description="Deadline for the task")
    project_id: int = Field(..., description="The ID of the project this task is associated with", examples=[1])
    parent_id: Optional[int] = Field(None, description="The ID of the parent task, if applicable", examples=[10])
    subtasks: list[SubtaskOutputSchema] = Field(default=[], description="Subtasks of this task (one level deep)")
    progress: float = Field(..., description="Automatic progress calculation based on completed subtasks (0-100%)", examples=[45.5])
    deleted_at: Optional[datetime] = Field(None, description="Timestamp when the task was deleted.")

    class Config:
        from_attributes = True


class ListDetailTaskOutputSchema(BaseModel):
    """
    Schema for returning a list of tasks with their full details.
    """
    tasks: list[DetailTaskOutputSchema] = Field(..., description="A list of tasks with their full details")


class TaskOutputSchema(BaseModel):
    """
    Schema returned after a task operation.
    """
    msg: str = Field(..., description="Informational message about the operation result", examples=["Task created successfully"])


class AssignUserTaskInputSchema(BaseModel):
    """
    Schema for assigning a user to a task.
    """
    user_id: int = Field(..., description="The ID of the user to be assigned to the task", examples=[10])
