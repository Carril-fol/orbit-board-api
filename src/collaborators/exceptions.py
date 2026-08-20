class CollaboratorNotFound(Exception):
    pass


class CollaboratorAlreadyExists(Exception):
    def __init__(self):
        super().__init__("This user is already a collaborator of this project")


class CollaboratorNotAuthorized(Exception):
    def __init__(self):
        super().__init__("You are not a collaborator of this project")


class CollaboratorProjectInsufficientPrivileges(Exception):
    def __init__(self):
        super().__init__("You are not the owner of this project")
