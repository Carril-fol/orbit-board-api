class ProjectInvitationAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("Invite already exists.")


class ProjectInvitationNotFoundError(Exception):
    def __init__(self):
        super().__init__("Invite not found")
        

class ProjectInvitationPermissionError(Exception):
    def __init__(self):
        super().__init__("You do not have permission to respond to this invitation.")


class ProjectInvitationNotAllowCollaborators(Exception):
    def __init__(self):
        super().__init__("Project does not allow collaborators.")


class ProjectInvitationIsAlreadyFull(Exception):
    def __init__(self):
        super().__init__("Project is full.")


class ProjectInvitationAlreadyResponded(Exception):
    def __init__(self):
        super().__init__("The invitation is not valid; it has already been responded to.")

