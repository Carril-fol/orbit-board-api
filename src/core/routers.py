from fastapi import FastAPI

from auth.controllers.auth_controller import router as auth_router
from collaborators.controllers.collaborators_controller import router as collaborators_router
from project_invitations.controllers.project_invitation_controller import router as project_invitation_router
from projects.controllers.project_controller import router as project_router
from projects_tags.controllers.project_tag_controller import router as project_tag_router
from requests.controllers.requests_controller import router as requests_router
from tasks.controllers.task_controller import router as tasks_router
from comments.controllers.comment_controller import router as comments_router
from tasks.controllers.task_user_controller import router as tasks_user_router

def register_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(project_router)
    app.include_router(project_tag_router)
    app.include_router(collaborators_router)
    app.include_router(project_invitation_router)
    app.include_router(requests_router)
    app.include_router(tasks_router)
    app.include_router(comments_router)
    app.include_router(tasks_user_router)