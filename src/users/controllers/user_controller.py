from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

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
@limiter.limit("10/minute")
async def get_authenticated_user(
    request: Request,
    service: IUserService = Depends(get_user_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    return await service.get_user_by_id(user_id)
