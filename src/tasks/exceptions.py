from core.exceptions import DomainError


class TaskNotFound(DomainError):
    status_code = 404
    detail = "Task not found"


class TaskUserHasNotPermission(DomainError):
    status_code = 403
    detail = "User does not have permission"


class TaskUserIsNotAnCollaborator(DomainError):
    status_code = 403
    detail = "User is not a collaborator"


class TaskUserAlreadyStatusAssigned(DomainError):
    status_code = 400
    detail = "The user already has this status assigned to the task"


class TaskCannotCompleted(DomainError):
    status_code = 400
    detail = "Cannot complete task while subtasks are still open"


class TaskInvalidParent(DomainError):
    status_code = 400
    detail = "Subtasks are one level deep: the parent must be another top-level task, and a task with subtasks cannot become one"


class TaskUserNotFound(DomainError):
    status_code = 404
    detail = "This register not exists"
