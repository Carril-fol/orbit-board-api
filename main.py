from uvicorn import run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.exception_handlers import (
    register_exception_handlers,
    register_invitation_exception_handlers,
    register_project_exception_handlers,
    register_comments_exception_handlers,
    register_collaborators_exception_handlers,
    register_tasks_exception_handlers,
    register_project_tag_exception_handlers,
    register_auth_exception_handlers,
    register_request_exception_handlers
)
from core.routers import register_routers
from core.logging import LoggingMiddleware
from shared.config.settings import settings
from shared.extensions import limiter


def create_app() -> FastAPI:
    app = FastAPI(
        title="Orbit Board API",
        description=(
            "Orbit Board is a project management API designed to create workspaces, "
            "publish them to attract collaborators or invite specific individuals, and "
            "manage workflows through a system of hierarchical tasks and comments."
            "\n\n"
            "### Authentication\n"
            "Tokens are delivered as **HttpOnly cookies**, never in the response body, "
            "so the *Authorize* button has nothing to type into. To use the protected "
            "endpoints from this page, run `POST /auth/api/v1/login` with **Try it out**: "
            "the browser keeps the cookie and sends it on every request you make from "
            "the docs afterwards. `POST /auth/api/v1/logout` clears it again."
        ),
        contact={
            "name": "Folco Carril",
            "url": "https://folcocarril.dev"
        },
        docs_url="/docs",
        swagger_ui_parameters={
            # Send cookies with "Try it out" requests even when the docs are opened
            # from a different origin than the API.
            "withCredentials": True,
            "persistAuthorization": True,
        },
    )
    app.state.limiter = limiter

    register_project_exception_handlers(app)
    register_invitation_exception_handlers(app)
    register_comments_exception_handlers(app)
    register_collaborators_exception_handlers(app)
    register_tasks_exception_handlers(app)
    register_project_tag_exception_handlers(app)
    register_exception_handlers(app)
    register_auth_exception_handlers(app)
    register_request_exception_handlers(app)

    register_routers(app)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_supports_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(LoggingMiddleware)
    return app


app = create_app()

@app.get("/health", tags=["Health"], summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok"}

if __name__ == "__main__":
    run(
        app,
        host=settings.server_host,
        port=settings.server_port,
    )