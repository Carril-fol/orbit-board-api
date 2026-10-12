from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required, CurrentUserId
from shared.extensions import limiter, READ_LIMIT, WRITE_LIMIT
from shared.pagination import Pagination

from ..dependencies import get_project_service
from ..interfaces import IProjectService
from ..schemas.project_schema import (
    DeleteProjectOutputSchema,
    ListProjectDetail,
    ProjectDetail,
    RegisterProjectInputSchema,
    RegisterProjectOutputSchema,
    UpdateProjectInputSchema,
    UpdateProjectOutputSchema,
)

router = APIRouter(
    prefix="/projects/api/v1",
    tags=["Projects"],
    dependencies=[
        Depends(jwt_required),
    ],
)


@router.post("/", response_model=RegisterProjectOutputSchema, status_code=201)
@limiter.limit(WRITE_LIMIT)
async def create_project(
    user_id: CurrentUserId,
    request: Request,
    data: RegisterProjectInputSchema,
    service: IProjectService = Depends(get_project_service),
):
    await service.create_project(data, user_id)
    return RegisterProjectOutputSchema(msg="Project created successfully")


@router.get("/", response_model=ListProjectDetail, status_code=200)
@limiter.limit(READ_LIMIT)
async def get_all_project(
    request: Request,
    page: Pagination,
    service: IProjectService = Depends(get_project_service),
):
    return await service.get_all_project(page.limit, page.offset)


@router.get("/me", response_model=ListProjectDetail, status_code=200)
@limiter.limit(READ_LIMIT)
async def get_my_projects(
    user_id: CurrentUserId,
    request: Request,
    page: Pagination,
    service: IProjectService = Depends(get_project_service),
):
    return await service.get_projects_for_user(user_id, page.limit, page.offset)


@router.get("/{project_id}", response_model=ProjectDetail, status_code=200)
@limiter.limit(READ_LIMIT)
async def get_project(
    user_id: CurrentUserId,
    request: Request,
    project_id: int,
    service: IProjectService = Depends(get_project_service),
):
    return await service.detail_project_by_id(project_id, user_id)


@router.patch("/{project_id}", response_model=UpdateProjectOutputSchema, status_code=200)
@limiter.limit(WRITE_LIMIT)
async def update_project(
    user_id: CurrentUserId,
    request: Request,
    project_id: int,
    data: UpdateProjectInputSchema,
    service: IProjectService = Depends(get_project_service),
):
    await service.update_project(project_id, data, user_id)
    return UpdateProjectOutputSchema(msg="Project updated")


@router.delete("/{project_id}", response_model=DeleteProjectOutputSchema, status_code=200)
@limiter.limit(WRITE_LIMIT)
async def delete_project(
    user_id: CurrentUserId,
    request: Request,
    project_id: int,
    service: IProjectService = Depends(get_project_service),
):
    await service.delete_project(project_id, user_id)
    return DeleteProjectOutputSchema(msg="Project deleted successfully")
