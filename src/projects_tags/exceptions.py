class ProjectTagNotFound(Exception):
    pass
class ProjectNotFound(Exception):
    def __init__(self):
        super().__init__("Project tag not found")
