from fastapi import APIRouter, Depends, Query, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

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
    request: Request,
    project_id: int,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of entries to return."),
    offset: int = Query(0, ge=0, description="Number of entries to skip."),
    service: IAuditLogService = Depends(get_audit_log_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    return await service.get_project_logs(project_id, user_id, limit, offset)
