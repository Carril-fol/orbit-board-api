import jwt
from uuid import uuid4
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie

from shared.config.settings import settings


class JwtManager:
    SECRET_KEY = settings.secret_key
    ALGORITHM = "HS256"

    EXPIRES = {
        "access_token": settings.jwt_access_token_expires,
        "refresh_token": settings.jwt_refresh_token_expires,
    }

    @classmethod
    def create_token(cls, user_id: int, token_type: str) -> str:
        payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "type": token_type,
            "exp": datetime.now(timezone.utc)
            + timedelta(seconds=cls.EXPIRES[token_type]),
        }

        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

            return payload

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")

        except InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    @classmethod
    def validate_token(cls, token: str, type_wanted: str) -> dict:
        payload = cls.decode_token(token)

        if payload.get("type") != type_wanted:
            raise HTTPException(status_code=401, detail=f"Invalid {type_wanted} token")

        try:
            payload["sub"] = int(payload["sub"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token subject")

        return payload


def set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    for name, token, max_age in (
        ("access_token", access_token, settings.jwt_access_token_expires),
        ("refresh_token", refresh_token, settings.jwt_refresh_token_expires),
    ):
        response.set_cookie(
            key=name,
            value=token,
            max_age=max_age,
            httponly=settings.jwt_cookie_httponly,
            secure=settings.jwt_cookie_secure,
            samesite=settings.jwt_cookie_samesite.lower(),
        )


def clear_auth_cookies(response) -> None:
    for name in ("access_token", "refresh_token"):
        response.delete_cookie(
            key=name,
            httponly=settings.jwt_cookie_httponly,
            secure=settings.jwt_cookie_secure,
            samesite=settings.jwt_cookie_samesite.lower(),
        )


_COOKIE_AUTH_DESCRIPTION = (
    "Authentication travels in an **HttpOnly cookie**, so this field cannot set it: "
    "browsers do not let scripts write the `Cookie` header. "
    "Call `POST /auth/api/v1/login` right here in the docs instead — the browser "
    "stores the cookie and attaches it to every later request from this page."
)

access_token_cookie = APIKeyCookie(
    name="access_token",
    scheme_name="AccessTokenCookie",
    description=_COOKIE_AUTH_DESCRIPTION,
    auto_error=False,
)
refresh_token_cookie = APIKeyCookie(
    name="refresh_token",
    scheme_name="RefreshTokenCookie",
    description=_COOKIE_AUTH_DESCRIPTION,
    auto_error=False,
)


def get_access_token_from_cookie(token: str = Depends(access_token_cookie)) -> str:
    if not token:
        raise HTTPException(status_code=401, detail="Access token not found")
    return token


def get_refresh_token_from_cookie(token: str = Depends(refresh_token_cookie)) -> str:
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    return token


def jwt_required(token: str = Depends(get_access_token_from_cookie)):
    return JwtManager.validate_token(token, "access_token")


def jwt_refresh_required(token: str = Depends(get_refresh_token_from_cookie)):
    return JwtManager.validate_token(token, "refresh_token")