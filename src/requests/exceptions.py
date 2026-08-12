class RequestNotFound(Exception):
    def __init__(self):
        super().__init__("Request not found")


class RequestAlreadyExists(Exception):
    def __init__(self):
        super().__init__("Request already exists")

class RequestAlreadyRespondedError(Exception):
    def __init__(self):
        super().__init__("This request has already been responded to")


class RequestProjectNotFoundError(Exception):
    def __init__(self):
        super().__init__("Project not found")


class RequestCollaboratorAlreadyExists(Exception):
    def __init__(self):
        super().__init__("User already is a collaborator")


class RequestUserAlreadyIsInvited(Exception):
    def __init__(self):
        super().__init__("User is already invited to this project")