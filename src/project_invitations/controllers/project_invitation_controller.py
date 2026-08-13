from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..interfaces import IProjectInvitationService
from ..dependencies import get_project_invitation_service
from ..schemas.project_invitations_schemas import (
    CreateInvitationOutput,
    CreateProjectInvitation,
    ProjectInvitationOutput,
)


router = APIRouter(
    prefix="/invitations/api/v1",
    tags=["Invitations"],
    dependencies=[Depends(jwt_required)],
)


@router.post(
    "/create",
    response_model=CreateInvitationOutput,
    status_code=201,
)
@limiter.limit("20/minute")
async def create_invitation(
    request: Request,
    data: CreateProjectInvitation,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
    _payload: dict = Depends(jwt_required),
):
    inviter_id = _payload["sub"]
    token = await service.create_project_invitation(data, inviter_id)
    return CreateInvitationOutput(
        msg="Invitation created successfully.",
        token=token,
        accept_url=f"{router.prefix}/{token}/accept",
        reject_url=f"{router.prefix}/{token}/reject",
    )


@router.delete(
    "/remove/{id_invite}", response_model=ProjectInvitationOutput, status_code=200
)
async def remove_invitation(
    id_invite: int,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]

    await service.remove_project_invitation(id_invite, user_id)
    return ProjectInvitationOutput(msg="Invitation removed successfully.")


@router.post("/{token}/accept", response_model=ProjectInvitationOutput, status_code=200)
@limiter.limit("20/minute")
async def accept_invitation(
    request: Request,
    token: str,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]

    await service.respond_project_invitation(token, user_id, True)
    return ProjectInvitationOutput(msg="Invitation accepted successfully.")


@router.post("/{token}/reject", response_model=ProjectInvitationOutput, status_code=200)
@limiter.limit("20/minute")
async def reject_invitation(
    request: Request,
    token: str,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]

    await service.respond_project_invitation(token, user_id, False)
    return ProjectInvitationOutput(msg="Invitation rejected successfully.")
