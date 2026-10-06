from core.exceptions import DomainError


class NotificationNotFound(DomainError):
    status_code = 404
    detail = "Notification not found"
