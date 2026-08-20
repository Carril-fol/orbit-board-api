from projects.interfaces import IProjectAuthorizationService

from ..interfaces import IAuditLogService
from ..repositories.audit_log_repository import AuditLogRepository
from ..models.audit_log_model import AuditLog
from ..schemas.audit_log_schema import (
    AuditLogOutputSchema,
    ListAuditLogOutputSchema,
)


class AuditLogService(IAuditLogService):

    def __init__(
        self,
        repo: AuditLogRepository,
        project_authorization_service: IProjectAuthorizationService,
    ):
        self.repo = repo
        self.project_authorization_service = project_authorization_service

    async def _write(
        self, user_id: int, project_id: int, entity_type: str, entity_id: int,
        action: str, old_value: dict, new_value: dict,
    ) -> AuditLog:
        return await self.repo.create(AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
        ))

    async def record_diff(
        self, user_id, project_id, entity_type, entity_id, action, old_state, new_state
    ) -> AuditLog | None:
        diff_old = {}
        diff_new = {}

        for key, value in new_state.items():
            if key in old_state and old_state[key] != value:
                diff_old[key] = old_state[key]
                diff_new[key] = value

        if not diff_old:
            return None

        return await self._write(
            user_id, project_id, entity_type, entity_id, action, diff_old, diff_new
        )

    async def record_event(
        self, user_id, project_id, entity_type, entity_id, action, data
    ) -> AuditLog:
        return await self._write(
            user_id, project_id, entity_type, entity_id, action, {}, data
        )

    async def get_project_logs(
        self, project_id: int, user_id: int, limit: int, offset: int
    ) -> ListAuditLogOutputSchema:
        await self.project_authorization_service.require_project_owner(user_id, project_id)

        logs = await self.repo.get_by_project(project_id, limit, offset)
        total = await self.repo.count_by_project(project_id)

        return ListAuditLogOutputSchema(
            logs=[AuditLogOutputSchema.model_validate(log) for log in logs],
            total=total,
            limit=limit,
            offset=offset,
        )
