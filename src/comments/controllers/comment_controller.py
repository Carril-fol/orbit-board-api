from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import CurrentUserId
from shared.extensions import limiter
from shared.pagination import Pagination

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
    user_id: CurrentUserId,
    request: Request,
    data: RegisterCommentInputSchema,
    task_id: int,
    service: ICommentService = Depends(get_comments_service),
):
    await service.create_comment(data, user_id, task_id)
    return CommentOutputSchema(msg="Comment created")


@router.get(
    "/{comment_id}",
    response_model=DetailCommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def get_comment(
    user_id: CurrentUserId,
    request: Request,
    comment_id: int,
    service: ICommentService = Depends(get_comments_service),
):
    comment = await service.get_comment_by_id(comment_id, user_id)
    return comment


@task_comments_router.get(
    "/{task_id}/comments",
    response_model=ListDetailCommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def get_comment_from_tasks(
    user_id: CurrentUserId,
    request: Request,
    task_id: int,
    page: Pagination,
    service: ICommentService = Depends(get_comments_service),
):
    comments = await service.get_comments_by_task_id(task_id, user_id, page.limit, page.offset)
    return comments


@router.put(
    "/{comment_id}",
    response_model=CommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def update_comment(
    user_id: CurrentUserId,
    request: Request,
    data: UpdateCommentSchema,
    comment_id: int,
    service: ICommentService = Depends(get_comments_service),
):
    await service.update_comment(data, user_id, comment_id)
    return CommentOutputSchema(msg="Comment updated")


@router.delete(
    "/{comment_id}",
    response_model=CommentOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def delete_comment(
    user_id: CurrentUserId,
    request: Request,
    comment_id: int,
    service: ICommentService = Depends(get_comments_service),
):
    await service.delete_comment(comment_id, user_id)
    return CommentOutputSchema(msg="Comment deleted")