from core.exceptions import DomainError


class CollaboratorNotFound(DomainError):
    status_code = 404
    detail = "Collaborator not found"


class CollaboratorAlreadyExists(DomainError):
    status_code = 409
    detail = "This user is already a collaborator of this project"


class CollaboratorNotAuthorized(DomainError):
    status_code = 403
    detail = "You are not a collaborator of this project"


class CollaboratorProjectInsufficientPrivileges(DomainError):
    status_code = 403
    detail = "You are not the owner of this project"


class CollaboratorIsProjectOwner(DomainError):
    status_code = 409
    detail = "The project owner cannot leave or be removed from the project"
