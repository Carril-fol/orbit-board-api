from fastapi import APIRouter, Depends, Query, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

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
@limiter.limit("5/minute")
async def create_project(
    request: Request,
    data: RegisterProjectInputSchema,
    service: IProjectService = Depends(get_project_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    await service.create_project(data, user_id)
    return RegisterProjectOutputSchema(msg="Project created successfully")


@router.get("/", response_model=ListProjectDetail, status_code=200)
@limiter.limit("5/minute")
async def get_all_project(
    request: Request,
    per_page: int = Query(10, ge=1, le=100, description="Projects per page."),
    page: int = Query(1, ge=1, description="1-indexed page number."),
    service: IProjectService = Depends(get_project_service),
    payload: dict = Depends(jwt_required),
):
    list_detailed_projects = await service.get_all_project(per_page, page)
    return list_detailed_projects


@router.get("/me", response_model=ListProjectDetail, status_code=200)
@limiter.limit("5/minute")
async def get_my_projects(
    request: Request,
    per_page: int = Query(10, ge=1, le=100, description="Projects per page."),
    page: int = Query(1, ge=1, description="1-indexed page number."),
    service: IProjectService = Depends(get_project_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    return await service.get_projects_for_user(user_id, per_page, page)


@router.get("/{project_id}", response_model=ProjectDetail, status_code=200)
@limiter.limit("5/minute")
async def get_project(
    request: Request,
    project_id: int,
    service: IProjectService = Depends(get_project_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    return await service.detail_project_by_id(project_id, user_id)


@router.patch("/{project_id}", response_model=UpdateProjectOutputSchema, status_code=200)
@limiter.limit("5/minute")
async def update_project(
    request: Request,
    project_id: int,
    data: UpdateProjectInputSchema,
    service: IProjectService = Depends(get_project_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    await service.update_project(project_id, data, user_id)
    return UpdateProjectOutputSchema(msg="Project updated")


@router.delete("/{project_id}", response_model=DeleteProjectOutputSchema, status_code=200)
@limiter.limit("5/minute")
async def delete_project(
    request: Request,
    project_id: int,
    service: IProjectService = Depends(get_project_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    await service.delete_project(project_id, user_id)
    return DeleteProjectOutputSchema(msg="Project deleted successfully")
