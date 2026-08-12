class ProjectNotFoundError(Exception):
    pass


class ProjectInsufficientPrivileges(Exception):
    def __init__(self):
        super().__init__("You don't have privileges for this action.")


class ProjectAlreadyHasStatus(Exception):
    def __init__(self):
        super().__init__("The project has already been cancelled.")