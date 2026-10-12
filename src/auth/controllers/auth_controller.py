from fastapi import APIRouter, Depends, Request, Response

from core.security.jwt_manager import (
    JwtManager,
    jwt_refresh_required,
    access_token_cookie,
    refresh_token_cookie,
    set_auth_cookies,
    clear_auth_cookies,
)
from shared.extensions import limiter, AUTH_LIMIT, WRITE_LIMIT

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
@limiter.limit(AUTH_LIMIT)
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
@limiter.limit(AUTH_LIMIT)
async def login(
    request: Request,
    data: LoginInputSchema,
    response: Response,
    service: IAuthService = Depends(get_auth_service),
    jwt_manager: JwtManager = Depends(),
):
    user_id = await service.authenticate(data)

    access_token = jwt_manager.create_token(user_id, "access_token")
    refresh_token = jwt_manager.create_token(user_id, "refresh_token")

    set_auth_cookies(response, access_token, refresh_token)
    return AuthOutputSchema(msg="Login successfully")


@router.post(
    "/logout", 
    response_model=AuthOutputSchema, 
    status_code=200
)
@limiter.limit(WRITE_LIMIT)
async def logout(
    request: Request,
    response: Response,
    access_token: str | None = Depends(access_token_cookie),
    refresh_token: str | None = Depends(refresh_token_cookie),
    service: IAuthService = Depends(get_auth_service),
):
    await service.logout(access_token, refresh_token)
    clear_auth_cookies(response)
    return AuthOutputSchema(msg="Logout successfully")


@router.post(
    "/refresh",
    response_model=AuthOutputSchema,
    status_code=200,
)
@limiter.limit(WRITE_LIMIT)
async def refresh(
    request: Request,
    response: Response,
    _payload: dict = Depends(jwt_refresh_required),
    service: IAuthService = Depends(get_auth_service),
):
    await service.rotate_refresh_token(_payload)
    user_id = _payload["sub"]
    access_token = JwtManager.create_token(user_id, "access_token")
    refresh_token = JwtManager.create_token(user_id, "refresh_token")

    set_auth_cookies(response, access_token, refresh_token)
    return AuthOutputSchema(msg="Token refreshed successfully")
