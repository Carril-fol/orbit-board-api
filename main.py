from fastapi import FastAPI
from uvicorn import run

from core.exception_handlers import (
    register_exception_handlers,
    register_invitation_exception_handlers,
    register_project_exception_handlers,
    register_comments_exception_handlers,
    register_tasks_exception_handlers
)
from core.lifespan import lifespan
from core.routers import register_routers
from shared.extensions import limiter


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.state.limiter = limiter

    register_project_exception_handlers(app)
    register_invitation_exception_handlers(app)
    register_comments_exception_handlers(app)
    register_tasks_exception_handlers(app)
    register_exception_handlers(app)

    register_routers(app)
    return app


app = create_app()

if __name__ == "__main__":
    run(
        app,
        #host="0.0.0.0",
        port=8000,
    )