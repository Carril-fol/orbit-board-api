from core.exceptions import DomainError


class ProjectNotFoundError(DomainError):
    status_code = 404
    detail = "Project not found."


class ProjectInsufficientPrivileges(DomainError):
    status_code = 403
    detail = "You don't have privileges for this action."


class ProjectAlreadyHasStatus(DomainError):
    status_code = 400
    detail = "The project has already been canceled."


class ProjectIsCanceled(DomainError):
    status_code = 409
    detail = "The project is canceled."


class ProjectIsFull(DomainError):
    status_code = 409
    detail = "The project is currently full."
