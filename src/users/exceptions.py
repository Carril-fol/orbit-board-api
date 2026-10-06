from core.exceptions import DomainError


class UserNotFound(DomainError):
    status_code = 404
    detail = "User not found."
