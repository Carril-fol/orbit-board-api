from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..dependencies import get_project_tag_service
from ..schemas.project_tag_schema import (
    ProjectTagOutputSchema,
    RegisterProjectTagInputSchema,
)
from ..services.project_tag_service import ProjectTagService

router = APIRouter(
    prefix="/projects-tags/api/v1",
    tags=["Projects tags"],
    dependencies=[Depends(jwt_required)],
)


@router.post(
    "/create/{project_id}",
    response_model=ProjectTagOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
def create_project_tag(
    request: Request,
    project_id: int,
    data: RegisterProjectTagInputSchema,
    service: ProjectTagService = Depends(get_project_tag_service),
    payload: dict = Depends(jwt_required),
):
    user_id = payload["sub"]
    service.create_project_tag(project_id, data, user_id)
    return ProjectTagOutputSchema(msg="Project tag created")


@router.delete(
    "/delete/{id_tag}",
    response_model=ProjectTagOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
def delete_project_tag(
    request: Request,
    id_tag: int,
    service: ProjectTagService = Depends(get_project_tag_service),
    payload: dict = Depends(jwt_required),
):
    user_id = payload["sub"]
    service.delete_tag_from_project(id_tag, user_id)
    return ProjectTagOutputSchema(msg="Project tag deleted")
