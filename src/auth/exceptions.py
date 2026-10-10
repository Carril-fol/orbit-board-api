from core.exceptions import DomainError


class InvalidCredentialsException(DomainError):
    status_code = 401
    detail = "Invalid credentials"


class InvalidTokenExceptions(DomainError):
    status_code = 401
    detail = "Invalid token"


class AuthUserAlreadyExistWithThatEmail(DomainError):
    status_code = 409
    detail = "An User already has this email"


class AuthUserAlreadyExistWithThatUsername(DomainError):
    status_code = 409
    detail = "An User already has this username"
