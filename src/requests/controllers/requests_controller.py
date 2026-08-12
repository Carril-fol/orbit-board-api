from fastapi import APIRouter, Depends, Request
from fastapi_cache.decorator import cache

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..services.requests_services import RequestsService
from ..dependencies import get_requests_service
from ..schemas.requests_schemas import (
    DetailRequestSchema,
    ListDetailRequestSchema,
    RegisterRequestsInputSchema,
    RequestOutputSchema,
)

router = APIRouter(
    prefix="/requests/api/v1",
    tags=["Requests"],
    dependencies=[Depends(jwt_required)],
)


@router.post(
    "/create/{project_id}",
    response_model=RequestOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
async def create(
    request: Request,
    data: RegisterRequestsInputSchema,
    project_id: int,
    service: RequestsService = Depends(get_requests_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    await service.create_request(data, user_id, project_id)
    return RequestOutputSchema(msg="Request created successfully")


@router.post(
    "/approve/{request_id}",
    response_model=RequestOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
async def approve(
    request: Request,
    request_id: int,
    service: RequestsService = Depends(get_requests_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    await service.respond_request(request_id, user_id, True)
    return RequestOutputSchema(msg="Request approved successfully")


@router.post(
    "/decline/{request_id}",
    response_model=RequestOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def decline(
    request: Request,
    request_id: int,
    service: RequestsService = Depends(get_requests_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    await service.respond_request(request_id, user_id, False)
    return RequestOutputSchema(msg="Request declined successfully")

@router.get(
    "/all/{project_id}",
    response_model=ListDetailRequestSchema,
    status_code=200,
)
@cache(expire=60)
@limiter.limit("10/minute")
async def get_all(
    request: Request,
    project_id: int,
    service: RequestsService = Depends(get_requests_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    requests = await service.get_all_requests(project_id, user_id)
    return ListDetailRequestSchema(requests=requests)


@router.get(
    "/{request_id}",
    response_model=DetailRequestSchema,
    status_code=200,
)
@cache(expire=120)
@limiter.limit("10/minute")
async def get_request(
    request: Request,
    request_id: int,
    service: RequestsService = Depends(get_requests_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    request = await service.get_request(request_id, user_id)
    return request
