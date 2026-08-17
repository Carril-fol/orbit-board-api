from fastapi import APIRouter, Depends, Request, Response

from core.security.jwt_manager import (
    JwtManager,
    jwt_required,
    jwt_refresh_required,
    set_auth_cookies,
    clear_auth_cookies,
)
from shared.extensions import limiter

from ..dependencies import get_auth_service
from ..schemas.auth_schema import (
    AuthOutputSchema,
    LoginInputSchema,
    RegisterInputSchema,
)
from ..interfaces import IAuthService

router = APIRouter(prefix="/auth/api/v1", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthOutputSchema,
    status_code=201,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterInputSchema,
    service: IAuthService = Depends(get_auth_service),
):
    await service.register_user(data)
    return AuthOutputSchema(msg="Register successfully")


@router.post(
    "/login",
    response_model=AuthOutputSchema,
    status_code=200,
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: LoginInputSchema,
    response: Response,
    service: IAuthService = Depends(get_auth_service),
    jwt_manager: JwtManager = Depends(),
):
    user_id = await service.authenticate(data)

    access_token = jwt_manager.create_access_token(user_id=user_id)
    refresh_token = jwt_manager.create_refresh_token(user_id=user_id)

    # The tokens only ever leave through HttpOnly cookies. Returning them in the
    # body too would hand them straight back to any script on the page and
    # undo the reason for making the cookies HttpOnly in the first place.
    set_auth_cookies(response, access_token, refresh_token)
    return AuthOutputSchema(msg="Login successfully")


@router.post(
    "/logout", 
    response_model=AuthOutputSchema, 
    status_code=200
)
async def logout(
    response: Response, 
    _payload: dict = Depends(jwt_required)
):
    clear_auth_cookies(response)
    return AuthOutputSchema(msg="Logout successfully")


@router.get(
    "/refresh",
    response_model=AuthOutputSchema,
    status_code=200,
)
async def refresh(
    response: Response,
    _payload: dict = Depends(jwt_refresh_required),
):
    user_id = _payload["sub"]
    access_token = JwtManager.create_access_token(user_id=user_id)
    refresh_token = JwtManager.create_refresh_token(user_id=user_id)

    set_auth_cookies(response, access_token, refresh_token)
    return AuthOutputSchema(msg="Token refreshed successfully")
