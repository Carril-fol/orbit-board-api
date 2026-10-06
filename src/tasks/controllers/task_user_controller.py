from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import CurrentUserId
from shared.extensions import limiter

from ..dependencies import get_task_user_service
from ..interfaces import ITaskUserService
from ..schemas.task_schemas import AssignUserTaskInputSchema, TaskOutputSchema


router = APIRouter(
    prefix="/tasks/api/v1",
    tags=["Task Users"],
)


@router.post(
    "/{task_id}/users",
    response_model=TaskOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def assign_user_to_task(
    actor_user_id: CurrentUserId,
    request: Request,
    task_id: int,
    data: AssignUserTaskInputSchema,
    service: ITaskUserService = Depends(get_task_user_service),
):
    await service.assign_user_to_task(
        task_id,
        data.user_id,
        actor_user_id,
    )
    return TaskOutputSchema(msg="User assigned to task")


@router.delete(
    "/{task_id}/users/{user_id}",
    response_model=TaskOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def unassign_user_from_task(
    actor_user_id: CurrentUserId,
    request: Request,
    task_id: int,
    user_id: int,
    service: ITaskUserService = Depends(get_task_user_service),
):
    await service.unassign_user_from_task(
        task_id,
        user_id,
        actor_user_id,
    )
    return TaskOutputSchema(msg="User unassigned from task")