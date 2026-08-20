from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from projects.exceptions import (
    ProjectAlreadyHasStatus,
    ProjectInsufficientPrivileges,
    ProjectNotFoundError,
    ProjectIsFull
)
from projects_tags.exceptions import ProjectNotFound, ProjectTagNotFound
from collaborators.exceptions import (
    CollaboratorAlreadyExists,
    CollaboratorNotAuthorized,
    CollaboratorNotFound,
    CollaboratorProjectInsufficientPrivileges,
)
from comments.exceptions import (
    CommentNotFound,
    CommentTaskNotFound,
    CommentUserIsNotFromProject,
    CommentUserHasNoPrivileges,
)
from tasks.exceptions import (
    TaskNotFound,
    TaskUserHasNotPermission,
    TaskUserIsNotAnCollaborator,
    TaskUserAlreadyStatusAssigned
)
from auth.exceptions import (
    InvalidCredentialsException,
    InvalidTokenExceptions,
    AuthUserAlreadyExistWithThatEmail
)
from project_invitations.exceptions import (
    ProjectInvitationPermissionError,
    ProjectInvitationAlreadyExistsError,
    ProjectInvitationNotFoundError,
    ProjectInvitationAlreadyResponded
)
from users.exceptions import UserNotFound
from requests.exceptions import (
    RequestCollaboratorAlreadyExists,
    RequestAlreadyExists,
    RequestAlreadyRespondedError,
    RequestNotFound,
    RequestUserAlreadyIsInvited,
    RequestProjectNotFoundError
)

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def register_user_exception_handlers(app):

    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(request: Request, exc: UserNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})


def register_invitation_exception_handlers(app):
    @app.exception_handler(ProjectInvitationPermissionError)
    async def permission_handler(request: Request, exc: ProjectInvitationPermissionError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(ProjectInvitationAlreadyExistsError)
    async def already_exists_handler(request: Request, exc: ProjectInvitationAlreadyExistsError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ProjectInvitationNotFoundError)
    async def not_found_handler(request: Request, exc: ProjectInvitationNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ProjectInvitationAlreadyResponded)
    async def already_responded_handler(request: Request, exc: ProjectInvitationAlreadyResponded):
        return JSONResponse(status_code=400, content={"detail": str(exc)})


def register_project_exception_handlers(app):

    @app.exception_handler(ProjectNotFoundError)
    async def not_found_handler(request: Request, exc: ProjectNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ProjectInsufficientPrivileges)
    async def insufficient_privileges_handler(
        request: Request, exc: ProjectInsufficientPrivileges
    ):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(ProjectAlreadyHasStatus)
    async def already_has_status_handler(
        request: Request, exc: ProjectAlreadyHasStatus
    ):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    
    @app.exception_handler(ProjectIsFull)
    async def project_is_full_handler(
        request: Request, exc: ProjectIsFull
    ):
        return JSONResponse(status_code=409, content={"detail": str(exc)})


def register_request_exception_handlers(app):

    @app.exception_handler(RequestNotFound)
    async def request_not_found_handler(request: Request, exc: RequestNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(RequestProjectNotFoundError)
    async def request_project_not_found_handler(request: Request, exc: RequestProjectNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(RequestCollaboratorAlreadyExists)
    async def request_collaborator_already_exists_handler(
        request: Request, exc: RequestCollaboratorAlreadyExists
    ):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RequestAlreadyExists)
    async def request_already_exists_handler(
        request: Request, exc: RequestAlreadyExists
    ):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RequestUserAlreadyIsInvited)
    async def request_user_already_is_invited_handler(
        request: Request, exc: RequestUserAlreadyIsInvited
    ):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RequestAlreadyRespondedError)
    async def request_already_responded_handler(
        request: Request, exc: RequestAlreadyRespondedError
    ):
        return JSONResponse(status_code=400, content={"detail": str(exc)})



def register_project_tag_exception_handlers(app):
    
    @app.exception_handler(ProjectTagNotFound)
    async def project_tag_not_found_handler(request: Request, exc: ProjectTagNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(ProjectNotFound)
    async def project_not_found_handler(request: Request, exc: ProjectNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})


def register_tasks_exception_handlers(app):
    
    @app.exception_handler(TaskNotFound)
    async def task_not_found_handler(request: Request, exc: TaskNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    
    @app.exception_handler(TaskUserIsNotAnCollaborator)
    async def task_user_is_not_an_collaborator(request: Request, exc: TaskUserIsNotAnCollaborator):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    
    @app.exception_handler(TaskUserHasNotPermission)
    async def task_user_has_not_permission(request: Request, exc: TaskUserHasNotPermission):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    
    @app.exception_handler(TaskUserAlreadyStatusAssigned)
    async def task_user_already_has_status(request: Request, exc: TaskUserAlreadyStatusAssigned):
        return JSONResponse(status_code=400, content={"detail": str(exc)})


def register_collaborators_exception_handlers(app):

    @app.exception_handler(CollaboratorNotFound)
    async def collaborator_not_found_handler(request: Request, exc: CollaboratorNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(CollaboratorNotAuthorized)
    async def collaborator_not_authorized_handler(request: Request, exc: CollaboratorNotAuthorized):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(CollaboratorProjectInsufficientPrivileges)
    async def collaborator_insufficient_privileges_handler(
        request: Request, exc: CollaboratorProjectInsufficientPrivileges
    ):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(CollaboratorAlreadyExists)
    async def collaborator_already_exists_handler(
        request: Request, exc: CollaboratorAlreadyExists
    ):
        return JSONResponse(status_code=409, content={"detail": str(exc)})


def register_comments_exception_handlers(app):
    
    @app.exception_handler(CommentNotFound)
    async def comment_not_found_handler(request: Request, exc: CommentNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    
    @app.exception_handler(CommentTaskNotFound)
    async def comment_task_not_found(request: Request, exc: CommentTaskNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    
    @app.exception_handler(CommentUserIsNotFromProject)
    async def comment_user_is_not_from_project(request: Request, exc: CommentUserIsNotFromProject):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    
    @app.exception_handler(CommentUserHasNoPrivileges)
    async def comment_user_has_not_privileges(request: Request, exc: CommentUserHasNoPrivileges):
        return JSONResponse(status_code=403, content={"detail": str(exc)})


def register_auth_exception_handlers(app):
    
    @app.exception_handler(AuthUserAlreadyExistWithThatEmail)
    async def user_already_exist_with_that_email(request: Request, exc: AuthUserAlreadyExistWithThatEmail):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    
    @app.exception_handler(InvalidTokenExceptions)
    async def invalid_token(request: Request, exc: InvalidTokenExceptions):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    
    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials(request: Request, exc: InvalidCredentialsException):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    