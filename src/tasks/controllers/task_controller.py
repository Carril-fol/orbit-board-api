from fastapi import APIRouter, Depends, Request
from fastapi_cache.decorator import cache

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..dependencies import get_task_service
from ..schemas.task_schemas import (
    RegisterTaskInputSchema,
    DetailTaskOutputSchema,
    ListDetailTaskOutputSchema,
    UpdateTaskInputSchema,
    TaskOutputSchema,
    AssignUserTaskInputSchema
)
from ..services.task_service import TaskService

router = APIRouter(prefix="/tasks/api/v1", tags=["tasks"])


@router.post(
    "/create/{project_id}",
    response_model=TaskOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
async def create_task(
    request: Request,
    data: RegisterTaskInputSchema,
    project_id: int,
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    user_id = payload["sub"]
    service.create(data, user_id, project_id)
    return TaskOutputSchema(msg="Task created")


@router.get(
    "/get/{task_id}",
    response_model=DetailTaskOutputSchema,
    status_code=200,
)
@cache(expire=60)
@limiter.limit("10/minute")
async def get_task(
    request: Request,
    task_id: int,
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    user_id = payload["sub"]
    task = service.get_task_by_id(task_id, user_id)
    return task


@router.get(
    "/get/all/{project_id}",
    response_model=ListDetailTaskOutputSchema,
    status_code=200,
)
@cache(expire=60)
@limiter.limit("10/minute")
async def get_tasks(
    request: Request,
    project_id: int,
    status: str = None,
    priority: str = None,
    user_id: int = None,
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    current_user_id = payload["sub"]
    tasks = service.get_tasks_by_project(
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
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    user_id = payload["sub"]
    service.delete_task(task_id, user_id)
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
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    user_id = payload["sub"]
    service.update_task(task_id, data, user_id)
    return TaskOutputSchema(msg="Task updated")


@router.post(
    "/assign/{task_id}/",
    response_model=TaskOutputSchema,
    status_code=200,
)
async def assign_user_to_task(
    request: Request,
    task_id: int,
    data: AssignUserTaskInputSchema,
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    actor_user_id = payload["sub"]
    a = service.assign_user_to_task(task_id, data.user_id, actor_user_id)
    print(a)
    return TaskOutputSchema(msg="User assigned to task")


@router.delete(
    "/unassign/{task_id}/",
    response_model=TaskOutputSchema,
    status_code=200,
)
async def unassign_user_from_task(
    request: Request,
    task_id: int,
    data: AssignUserTaskInputSchema,
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    actor_user_id = payload["sub"]
    service.unassign_user_from_task(task_id, data.user_id, actor_user_id)
    return TaskOutputSchema(msg="User unassigned from task")


@router.get(
    "/get/search/{search_term}",
    response_model=ListDetailTaskOutputSchema,
    status_code=200,
)
@cache(expire=60)
@limiter.limit("10/minute")
async def get_tasks_by_title_or_description(
    request: Request,
    search_term: str,
    service: TaskService = Depends(get_task_service),
    payload: dict = Depends(jwt_required)
):
    tasks = service.get_tasks_by_title_or_description(search_term)
    return tasks

