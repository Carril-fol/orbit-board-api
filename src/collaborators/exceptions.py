class CollaboratorNotFound(Exception):
    pass


class CollaboratorAlreadyExists(Exception):
    pass


class CollaboratorNotAuthorized(Exception):
    def __init__(self):
        super().__init__("You are not a collaborator of this project")


class CollaboratorProjectInsufficientPrivileges(Exception):
    def __init__(self):
        super().__init__("You are not the owner of this project")
        
        
class CollaboratorProjectNotFoundError(Exception):
    def __init__(self):
        super().__init__("Project not found")
        