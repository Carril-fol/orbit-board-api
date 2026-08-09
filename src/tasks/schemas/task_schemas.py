from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from ..models.task_model import TaskPriority, TaskStatus
from ..models.task_user_model import TaskUserStatus


class TaskBaseSchema(BaseModel):
    title: str = Field(..., description="The title of the task", example="Implement User Authentication")
    description: Optional[str] = Field(None, description="Detailed description of the task requirements", example="Create JWT based auth system with refresh tokens")
    status: TaskStatus = Field(..., description="The current state of the task (TO DO, IN PROGRESS, REVIEW, DONE)")
    priority: TaskPriority = Field(..., description="Priority level of the task (LOW, MEDIUM, HIGH)")
    expiration_date: Optional[datetime] = Field(None, description="Optional deadline for the task completion")

class RegisterTaskInputSchema(TaskBaseSchema):
    parent_id: Optional[int] = Field(None, description="The ID of the parent task if this is a subtask")


class CreateTaskInputSchema(TaskBaseSchema):
    project_id: int = Field(..., description="The ID of the project this task belongs to")
    parent_id: Optional[int] = Field(None, description="The ID of the parent task for hierarchical structure")


class UpdateTaskInputSchema(BaseModel):
    title: Optional[str] = Field(None, description="Updated title of the task")
    description: Optional[str] = Field(None, description="Updated description")
    status: Optional[TaskStatus] = Field(None, description="New status of the task")
    priority: Optional[TaskPriority] = Field(None, description="New priority level")
    expiration_date: Optional[datetime] = Field(None, description="New expiration date")
    parent_id: Optional[int] = Field(None, description="Change the parent task of this task")


class DetailTaskOutputSchema(BaseModel):
    id: int = Field(..., description="The unique identifier of the task")
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    status: TaskStatus = Field(..., description="The current state of the task")
    priority: TaskPriority = Field(..., description="Priority level of the task")
    expiration_date: Optional[datetime] = Field(None, description="Deadline for the task")
    project_id: int = Field(..., description="The ID of the project this task is associated with")
    parent_id: Optional[int] = Field(None, description="The ID of the parent task, if applicable")
    subtasks: list["DetailTaskOutputSchema"] = Field(default=[], description="List of nested subtasks for this task")
    progress: float = Field(..., description="Automatic progress calculation based on completed subtasks (0-100%)")
    deleted_at: Optional[datetime] = Field(None, description="Optional deadline for the task completion")
    
    class Config:
        from_attributes = True


class ListDetailTaskOutputSchema(BaseModel):
    tasks: list[DetailTaskOutputSchema] = Field(..., description="A list of tasks with their full details")


class TaskOutputSchema(BaseModel):
    msg: str = Field(..., description="Informational message about the operation result")


class AssignUserTaskInputSchema(BaseModel):
    user_id: int = Field(..., description="The ID of the user to be assigned to the task")


class UpdateTaskUserInputSchema(BaseModel):
    user_id: int | None
    task_id: int
    status: TaskUserStatus