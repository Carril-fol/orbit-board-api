from abc import ABC, abstractmethod

from .models.audit_log_model import AuditLog
from .schemas.audit_log_schema import ListAuditLogOutputSchema


class IAuditLogService(ABC):

    @abstractmethod
    async def record_diff(
        self,
        user_id: int,
        project_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        old_state: dict,
        new_state: dict
    ) -> AuditLog | None:
        pass

    @abstractmethod
    async def record_event(
        self,
        user_id: int,
        project_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        data: dict,
    ) -> AuditLog:
        pass

    @abstractmethod
    async def get_project_logs(
        self,
        project_id: int,
        user_id: int,
        limit: int,
        offset: int,
    ) -> ListAuditLogOutputSchema:
        pass
