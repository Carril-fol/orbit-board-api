from fastapi import APIRouter, Depends, Request
from fastapi_cache.decorator import cache

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..dependencies import get_project_service
from ..schemas.project_schema import (
    DeleteProjectOutputSchema,
    ListProjectDetail,
    ProjectDetail,
    RegisterProjectInputSchema,
    RegisterProjectOutputSchema,
    UpdateProjectInputSchema,
    UpdateProjectOutputSchema,
)
from ..services.project_service import ProjectService

router = APIRouter(
    prefix="/projects/api/v1",
    tags=["Projects"],
    dependencies=[
        Depends(jwt_required),
    ],
)


@router.post("/create", response_model=RegisterProjectOutputSchema, status_code=201)
@limiter.limit("5/minute")
def create_project(
    request: Request,
    data: RegisterProjectInputSchema,
    service: ProjectService = Depends(get_project_service),
    payload: dict = Depends(jwt_required),
):
    user_id = payload["sub"]
    service.create_project(data, user_id)
    return RegisterProjectOutputSchema(msg="Project created successfully")


@router.get("/get/{id}", response_model=ProjectDetail, status_code=200)
@cache(expire=30)
@limiter.limit("5/minute")
async def get_project(
    request: Request,
    id: int,
    service: ProjectService = Depends(get_project_service),
    payload: dict = Depends(jwt_required),
):
    project = service.detail_project_by_id(id)
    return project


@router.patch("/update/{id}", response_model=UpdateProjectOutputSchema, status_code=200)
@limiter.limit("5/minute")
def update_project(
    request: Request,
    id: int,
    data: UpdateProjectInputSchema,
    service: ProjectService = Depends(get_project_service),
    payload: dict = Depends(jwt_required),
):
    user_id = payload["sub"]
    service.update_project(id, data, user_id)
    return UpdateProjectOutputSchema(msg="Project updated")


@router.delete(
    "/delete/{id}", response_model=DeleteProjectOutputSchema, status_code=200
)
@limiter.limit("5/minute")
def delete_project(
    request: Request,
    id: int,
    service: ProjectService = Depends(get_project_service),
    payload: dict = Depends(jwt_required),
):
    user_id = payload["sub"]
    data = {"status": "CANCELLED"}
    service.delete_project(id, user_id, data)
    return DeleteProjectOutputSchema(msg="Project deleted successfully")


@router.get("/", response_model=ListProjectDetail, status_code=200)
@cache(expire=30)
@limiter.limit("5/minute")
async def get_all_project(
    request: Request,
    per_page: int = 10,
    page: int = 1,
    service: ProjectService = Depends(get_project_service),
    payload: dict = Depends(jwt_required),
):
    list_detailed_projects = service.get_all_project(per_page, page)
    return list_detailed_projects
