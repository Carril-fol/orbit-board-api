from core.exceptions import DomainError


class ProjectTagNotFound(DomainError):
    status_code = 404
    detail = "Project tag not found"


class ProjectNotFound(DomainError):
    status_code = 404
    detail = "Project tag not found"
