from fastapi import APIRouter, Depends, Request, Response

from core.security.jwt_manager import JwtManager, jwt_required
from shared.extensions import limiter

from ..dependencies import get_auth_service
from ..schemas.auth_schema import (
    AuthOutputSchema,
    LoginInputSchema,
    LoginOutputSchema,
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
    response_model=LoginOutputSchema,
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
    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="refresh_token", value=refresh_token)
    return LoginOutputSchema(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=AuthOutputSchema, status_code=200)
async def logout(response: Response, _payload: dict = Depends(jwt_required)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return AuthOutputSchema(msg="Logout successfully")


@router.get(
    "/refresh",
    response_model=LoginOutputSchema,
    status_code=200,
)
async def refresh(
    response: Response,
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    access_token = JwtManager.create_access_token(user_id=user_id)
    refresh_token = JwtManager.create_refresh_token(user_id=user_id)

    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="refresh_token", value=refresh_token)
    return LoginOutputSchema(access_token=access_token, refresh_token=refresh_token)
