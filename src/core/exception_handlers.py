from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.exceptions import DomainError


async def domain_error_handler(request: Request, exception: DomainError):
    return JSONResponse(status_code=exception.status_code, content={"detail": exception.detail})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_exception_handler(DomainError, domain_error_handler)
