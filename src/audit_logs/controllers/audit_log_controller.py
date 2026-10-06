from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required, CurrentUserId
from shared.extensions import limiter
from shared.pagination import Pagination

from ..dependencies import get_audit_log_service
from ..interfaces import IAuditLogService
from ..schemas.audit_log_schema import ListAuditLogOutputSchema

router = APIRouter(
    prefix="/projects/api/v1",
    tags=["Audit logs"],
    dependencies=[Depends(jwt_required)],
)


@router.get(
    "/{project_id}/audit-logs",
    response_model=ListAuditLogOutputSchema,
    status_code=200
)
@limiter.limit("10/minute")
async def get_project_audit_logs(
    user_id: CurrentUserId,
    request: Request,
    project_id: int,
    page: Pagination,
    service: IAuditLogService = Depends(get_audit_log_service),
):
    return await service.get_project_logs(project_id, user_id, page.limit, page.offset)
