from core.exceptions import DomainError


class AuthenticationError(DomainError):
    status_code = 401
    detail = "Not authenticated"


class TokenNotFound(AuthenticationError):
    detail = "Token not found"


class TokenExpired(AuthenticationError):
    detail = "Token expired"


class InvalidToken(AuthenticationError):
    detail = "Invalid token"


class TokenRevoked(AuthenticationError):
    detail = "Token revoked"
