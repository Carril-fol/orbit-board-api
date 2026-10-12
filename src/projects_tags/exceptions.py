from core.exceptions import DomainError


class ProjectTagNotFound(DomainError):
    status_code = 404
    detail = "Project tag not found"


class ProjectTagAlreadyExists(DomainError):
    status_code = 409
    detail = "The project already has this tag"
