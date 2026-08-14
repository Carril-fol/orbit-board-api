from abc import ABC, abstractmethod

from .models.audit_log_model import AuditLog


class IAuditLogService(ABC):

    @abstractmethod
    async def record_diff(
        self,
        user_id: int,
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
        entity_type: str,
        entity_id: int,
        action: str,
        data: dict,
    ) -> AuditLog:
        pass