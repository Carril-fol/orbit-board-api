class TaskNotFound(Exception):
    def __init__(self):
        super().__init__("Task not found")


class TaskUserHasNotPermission(Exception):
    def __init__(self):
        super().__init__("User does not have permission")


class TaskUserIsNotAnCollaborator(Exception):
    def __init__(self):
        super().__init__("User is not a collaborator")


class TaskCannotCompleted(Exception):
    def __init__(self):
        super().__init__("Cannot complete task while subtasks are still open")
class TaskUserAlreadyStatusAssigned(Exception):
    def __init__(self):
        super().__init__("The user already has this status assigned to the task")
        
        
class TaskUserNotFound(Exception):
    def __init__(self):
        super().__init__("This register not exists")
