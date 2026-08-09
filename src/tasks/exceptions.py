class TaskNotFound(Exception):
    def __init__(self, message="Task not found"):
        self.message = message
        
        
class TaskUserHasNotPermission(Exception):
    def __init__(self, message="User does not have permission"):
        self.message = message
        

class TaskUserIsNotAnCollaborator(Exception):
    def __init__(self, message="User is not an collaborator"):
        self.message = message
        
        
class TaskCannotCompleted(Exception):
    def __init__(self, message="Cannot complete task while subtasks are still open"):
        self.message = message
        

class TaskUserNotAssigned(Exception):
    def __init__(self, message="User not assigned to task"):
        self.message = message
        

class TaskUserAlreadyStatusAssigned(Exception):
    def __init__(self, message="The user already has this status assigned to the task"):
        self.message = message
        super().__init__(self.message)