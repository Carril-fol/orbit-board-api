from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required, CurrentUserId
from shared.extensions import limiter

from ..interfaces import IRequestsService
from ..dependencies import get_requests_service
from ..schemas.requests_schemas import (
    DetailRequestSchema,
    ListDetailRequestSchema,
    ListSentRequestSchema,
    RegisterRequestsInputSchema,
    RequestOutputSchema,
)

router = APIRouter(
    prefix="/requests/api/v1",
    tags=["Requests"],
    dependencies=[Depends(jwt_required)],
)
project_requests_router = APIRouter(
    prefix="/projects/api/v1",
    tags=["Requests"],
    dependencies=[Depends(jwt_required)],
)


@project_requests_router.post(
    "/{project_id}/requests",
    response_model=RequestOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
async def create(
    user_id: CurrentUserId,
    request: Request,
    data: RegisterRequestsInputSchema,
    project_id: int,
    service: IRequestsService = Depends(get_requests_service),
):
    await service.create_request(data, user_id, project_id)
    return RequestOutputSchema(msg="Request created successfully")


@router.post(
    "/{request_id}/approve",
    response_model=RequestOutputSchema,
    status_code=201,
)
@limiter.limit("10/minute")
async def approve(
    user_id: CurrentUserId,
    request: Request,
    request_id: int,
    service: IRequestsService = Depends(get_requests_service),
):
    await service.respond_request(request_id, user_id, True)
    return RequestOutputSchema(msg="Request approved successfully")


@router.post(
    "/{request_id}/decline",
    response_model=RequestOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def decline(
    user_id: CurrentUserId,
    request: Request,
    request_id: int,
    service: IRequestsService = Depends(get_requests_service),
):
    await service.respond_request(request_id, user_id, False)
    return RequestOutputSchema(msg="Request declined successfully")

@project_requests_router.get(
    "/{project_id}/requests",
    response_model=ListDetailRequestSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def get_all(
    user_id: CurrentUserId,
    request: Request,
    project_id: int,
    service: IRequestsService = Depends(get_requests_service),
):
    requests = await service.get_all_requests(project_id, user_id)
    return ListDetailRequestSchema(requests=requests)


@router.get(
    "/sent",
    response_model=ListSentRequestSchema,
    status_code=200,
    summary="Access requests submitted by the authenticated user",
)
@limiter.limit("10/minute")
async def get_sent(
    user_id: CurrentUserId,
    request: Request,
    service: IRequestsService = Depends(get_requests_service),
):
    requests = await service.get_sent_requests(user_id)
    return ListSentRequestSchema(requests=requests)


@router.get(
    "/{request_id}",
    response_model=DetailRequestSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def get_request(
    user_id: CurrentUserId,
    request: Request,
    request_id: int,
    service: IRequestsService = Depends(get_requests_service),
):
    request = await service.get_request(request_id, user_id)
    return request
