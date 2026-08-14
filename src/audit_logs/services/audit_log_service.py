from ..interfaces import IAuditLogService
from ..repositories.audit_log_repository import AuditLogRepository
from ..models.audit_log_model import AuditLog


class AuditLogService(IAuditLogService):

    def __init__(self, repo: AuditLogRepository):
        self.repo = repo

    async def _write(
        self, user_id: int, entity_type: str, entity_id: int,
        action: str, old_value: dict, new_value: dict,
    ) -> AuditLog:
        return await self.repo.create(AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
        ))

    async def record_diff(self, user_id, entity_type, entity_id, action, old_state, new_state) -> AuditLog | None:
        diff_old = {}
        diff_new = {}

        for key, value in new_state.items():
            if key in old_state and old_state[key] != value:
                diff_old[key] = old_state[key]
                diff_new[key] = value

        if not diff_old:
            return None

        return await self._write(user_id, entity_type, entity_id, action, diff_old, diff_new)

    async def record_event(self, user_id, entity_type, entity_id, action, data) -> AuditLog:
        return await self._write(user_id, entity_type, entity_id, action, {}, data)
