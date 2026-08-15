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
from core.lifespan import lifespan
from core.routers import register_routers
from shared.extensions import limiter


def create_app() -> FastAPI:
    app = FastAPI(
        title="Orbit Board API",
        description="Orbit Board is a project management API designed to create workspaces, publish them to attract collaborators or invite specific individuals, and manage workflows through a system of hierarchical tasks and comments.",
        contact={
            "name": "Folco Carril",
            "url": "https://folcocarril.dev"
        },
        lifespan=lifespan,
        docs_url="/docs"
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
    return app

app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

if __name__ == "__main__":
    run(
        app,
        host="0.0.0.0",
        port=8000,
    )