from core.exceptions import DomainError


class ProjectInvitationAlreadyExistsError(DomainError):
    status_code = 409
    detail = "Invite already exists."


class ProjectInvitationNotFoundError(DomainError):
    status_code = 404
    detail = "Invite not found"


class ProjectInvitationPermissionError(DomainError):
    status_code = 403
    detail = "You do not have permission to respond to this invitation."


class ProjectInvitationExpired(DomainError):
    status_code = 410
    detail = "The invitation has expired."


class ProjectInvitationAlreadyResponded(DomainError):
    status_code = 400
    detail = "The invitation is not valid; it has already been responded to."
