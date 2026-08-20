from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..dependencies import get_project_tag_service
from ..schemas.project_tag_schema import (
    ProjectTagOutputSchema,
    RegisterProjectTagInputSchema,
)
from ..interfaces import IProjectTagService

router = APIRouter(
    prefix="/project-tags/api/v1",
    tags=["Projects tags"],
    dependencies=[Depends(jwt_required)],
)
project_tags_router = APIRouter(
    prefix="/projects/api/v1",
    tags=["Projects tags"],
    dependencies=[Depends(jwt_required)],
)


@project_tags_router.post(
    "/{project_id}/tags",
    response_model=ProjectTagOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
async def create_project_tag(
    request: Request,
    project_id: int,
    data: RegisterProjectTagInputSchema,
    service: IProjectTagService = Depends(get_project_tag_service),
    payload: dict = Depends(jwt_required),
):
    user_id = payload["sub"]
    await service.create_project_tag(project_id, data, user_id)
    return ProjectTagOutputSchema(msg="Project tag created")


@router.delete(
    "/{tag_id}",
    response_model=ProjectTagOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def delete_project_tag(
    request: Request,
    tag_id: int,
    service: IProjectTagService = Depends(get_project_tag_service),
    payload: dict = Depends(jwt_required),
):
    user_id = payload["sub"]
    await service.delete_tag_from_project(tag_id, user_id)
    return ProjectTagOutputSchema(msg="Project tag deleted")
