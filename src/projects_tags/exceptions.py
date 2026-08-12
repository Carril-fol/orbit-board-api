class ProjectTagNotFound(Exception):
    pass


class ProjectTagNotAllowed(Exception):
    def __init__(self):
        super().__init__("Only the project owner can perform this action")


class ProjectNotFound(Exception):
    def __init__(self):
        super().__init__("Project tag not found")