from ..interfaces import IAuditLogService
from ..repositories.audit_log_repository import AuditLogRepository
from ..models.audit_log_model import AuditLog


class AuditLogService(IAuditLogService):

    def __init__(self, repo: AuditLogRepository):
        self.repo = repo
        
    async def record_diff(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        old_state: dict,
        new_state: dict
    ) -> AuditLog | None:
        diff_old = {}
        diff_new = {}

        for key in new_state:
            if key in old_state and old_state[key] != new_state[key]:
                diff_old[key] = old_state[key]
                diff_new[key] = new_state[key]

        if not diff_old:
            return None

        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=diff_old,
            new_value=diff_new
        )

        return await self.repo.create(audit_entry)