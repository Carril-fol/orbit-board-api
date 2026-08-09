from shared.database.base_repository import BaseRepository
from ..models.audit_log_model import AuditLog


class AuditLogRepository(BaseRepository[AuditLog]):
    
    def __init__(self, db):
        super().__init__(AuditLog, db)