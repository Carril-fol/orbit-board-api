from core.exceptions import DomainError


class RequestNotFound(DomainError):
    status_code = 404
    detail = "Request not found"


class RequestAlreadyExists(DomainError):
    status_code = 409
    detail = "Request already exists"


class RequestAlreadyRespondedError(DomainError):
    status_code = 400
    detail = "This request has already been responded to"


class RequestProjectNotFoundError(DomainError):
    status_code = 404
    detail = "Project not found."


class RequestCollaboratorAlreadyExists(DomainError):
    status_code = 409
    detail = "User already is a collaborator"


class RequestUserAlreadyIsInvited(DomainError):
    status_code = 409
    detail = "User is already invited to this project"
