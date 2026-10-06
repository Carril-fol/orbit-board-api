from core.exceptions import DomainError


class CommentNotFound(DomainError):
    status_code = 404
    detail = "Comment not found"


class CommentUserHasNoPrivileges(DomainError):
    status_code = 403
    detail = "Permission denied"
