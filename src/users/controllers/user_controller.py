from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import CurrentUserId
from shared.extensions import limiter, READ_LIMIT

from ..dependencies import get_user_service
from ..interfaces import IUserService
from ..schemas.user_schema import UserResponse

router = APIRouter(prefix="/users/api/v1", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=200,
    summary="Profile of the authenticated user",
)
@limiter.limit(READ_LIMIT)
async def get_authenticated_user(
    user_id: CurrentUserId,
    request: Request,
    service: IUserService = Depends(get_user_service),
):
    return await service.get_user_by_id(user_id)
