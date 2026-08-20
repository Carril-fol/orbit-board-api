from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..interfaces import ICommentService
from ..dependencies import get_comments_service
from ..schemas.comment_schema import (
    RegisterCommentInputSchema,
    CommentOutputSchema,
    ListDetailCommentOutputSchema,
    DetailCommentOutputSchema,
    UpdateCommentSchema
)

router = APIRouter(prefix="/comments/api/v1", tags=["Comments"])
task_comments_router = APIRouter(prefix="/tasks/api/v1", tags=["Comments"])


@task_comments_router.post(
    "/{task_id}/comments",
    response_model=CommentOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
async def create_comment(
    request: Request,
    data: RegisterCommentInputSchema,
    task_id: int,
    service: ICommentService = Depends(get_comments_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    await service.create_comment(data, user_id, task_id)
    return CommentOutputSchema(msg="Comment created")


@router.get(
    "/{comment_id}",
    response_model=DetailCommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def get_comment(
    request: Request,
    comment_id: int,
    service: ICommentService = Depends(get_comments_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    comment = await service.get_comment_by_id(comment_id, user_id)
    return comment


@task_comments_router.get(
    "/{task_id}/comments",
    response_model=ListDetailCommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def get_comment_from_tasks(
    request: Request,
    task_id: int,
    limit: int = 20,
    offset: int = 0,
    service: ICommentService = Depends(get_comments_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    comments = await service.get_comments_by_task_id(task_id, user_id, limit, offset)
    return comments


@router.put(
    "/{comment_id}",
    response_model=CommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def update_comment(
    request: Request,
    data: UpdateCommentSchema,
    comment_id: int,
    service: ICommentService = Depends(get_comments_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    await service.update_comment(data, user_id, comment_id)
    return CommentOutputSchema(msg="Comment updated")


@router.delete(
    "/{comment_id}",
    response_model=CommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def delete_comment(
    request: Request,
    comment_id: int,
    service: ICommentService = Depends(get_comments_service),
    _payload: dict = Depends(jwt_required)
):
    user_id = _payload["sub"]
    await service.delete_comment(comment_id, user_id)
    return CommentOutputSchema(msg="Comment deleted")