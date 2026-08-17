from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..dependencies import get_task_service
from ..interfaces import ITaskService

from ..schemas.task_schemas import (
    RegisterTaskInputSchema,
    DetailTaskOutputSchema,
    ListDetailTaskOutputSchema,
    UpdateTaskInputSchema,
    TaskOutputSchema,
)

router = APIRouter(prefix="/tasks/api/v1", tags=["Tasks"])


@router.post(
    "/create/{project_id}",
    response_model=TaskOutputSchema,
    status_code=201,
    summary="Create a new task",
    description="Create a new task v"
)
@limiter.limit("10/minute")
async def create_task(
    request: Request,
    data: RegisterTaskInputSchema,
    project_id: int,
    service: ITaskService = Depends(get_task_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    await service.create(data, user_id, project_id)
    return TaskOutputSchema(msg="Task created")


@router.get(
    "/get/{task_id}",
    response_model=DetailTaskOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def get_task(
    request: Request,
    task_id: int,
    service: ITaskService = Depends(get_task_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    task = await service.get_task_by_id(task_id, user_id)
    return task


@router.get(
    "/get/all/{project_id}",
    response_model=ListDetailTaskOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def get_tasks(
    request: Request,
    project_id: int,
    status: str = None,
    priority: str = None,
    user_id: int = None,
    service: ITaskService = Depends(get_task_service),
    _payload: dict = Depends(jwt_required)
):
    current_user_id = _payload["sub"]
    tasks = await service.get_tasks_by_project(
        current_user_id,
        project_id,
        status,
        priority,
        filter_user_id=user_id
    )
    return tasks


@router.delete(
    "/delete/{task_id}",
    response_model=TaskOutputSchema,
    status_code=200,
)
async def delete_task(
    request: Request,
    task_id: int,
    service: ITaskService = Depends(get_task_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    await service.delete_task(task_id, user_id)
    return TaskOutputSchema(msg="Task deleted")


@router.put(
    "/update/{task_id}",
    response_model=TaskOutputSchema,
    status_code=200,
)
async def update_task(
    request: Request,
    task_id: int,
    data: UpdateTaskInputSchema,
    service: ITaskService = Depends(get_task_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    await service.update_task(task_id, data, user_id)
    return TaskOutputSchema(msg="Task updated")

