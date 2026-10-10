from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from core.security.jwt_manager import CurrentUserId
from shared.extensions import limiter

from ..dependencies import get_task_service
from ..interfaces import ITaskService

from ..schemas.task_schemas import (
    RegisterTaskInputSchema,
    DetailTaskOutputSchema,
    ListDetailTaskOutputSchema,
    TaskFiltersSchema,
    UpdateTaskInputSchema,
    TaskOutputSchema,
)

router = APIRouter(prefix="/tasks/api/v1", tags=["Tasks"])
project_tasks_router = APIRouter(prefix="/projects/api/v1", tags=["Tasks"])


@project_tasks_router.post(
    "/{project_id}/tasks",
    response_model=TaskOutputSchema,
    status_code=201,
    summary="Create a new task",
    description="Create a new task v"
)
@limiter.limit("10/minute")
async def create_task(
    user_id: CurrentUserId,
    request: Request,
    data: RegisterTaskInputSchema,
    project_id: int,
    service: ITaskService = Depends(get_task_service),
):
    await service.create(data, user_id, project_id)
    return TaskOutputSchema(msg="Task created")


@router.get(
    "/{task_id}",
    response_model=DetailTaskOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def get_task(
    user_id: CurrentUserId,
    request: Request,
    task_id: int,
    service: ITaskService = Depends(get_task_service),
):
    task = await service.get_task_by_id(task_id, user_id)
    return task


@project_tasks_router.get(
    "/{project_id}/tasks",
    response_model=ListDetailTaskOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def get_tasks(
    current_user_id: CurrentUserId,
    request: Request,
    project_id: int,
    filters: Annotated[TaskFiltersSchema, Query()],
    service: ITaskService = Depends(get_task_service),
):
    tasks = await service.get_tasks_by_project(
        current_user_id,
        project_id,
        filters.limit,
        filters.offset,
        filters.status,
        filters.priority,
        filter_user_id=filters.user_id
    )
    return tasks


@router.delete(
    "/{task_id}",
    response_model=TaskOutputSchema,
    status_code=200,
)
async def delete_task(
    user_id: CurrentUserId,
    request: Request,
    task_id: int,
    service: ITaskService = Depends(get_task_service),
):
    await service.delete_task(task_id, user_id)
    return TaskOutputSchema(msg="Task deleted")


@router.put(
    "/{task_id}",
    response_model=TaskOutputSchema,
    status_code=200,
)
async def update_task(
    user_id: CurrentUserId,
    request: Request,
    task_id: int,
    data: UpdateTaskInputSchema,
    service: ITaskService = Depends(get_task_service),
):
    await service.update_task(task_id, data, user_id)
    return TaskOutputSchema(msg="Task updated")

