from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import jwt_required, CurrentUserId
from shared.extensions import limiter

from ..interfaces import IProjectInvitationService
from ..dependencies import get_project_invitation_service
from ..schemas.project_invitations_schemas import (
    CreateInvitationOutput,
    CreateProjectInvitation,
    ListReceivedInvitationSchema,
    ProjectInvitationOutput,
)


router = APIRouter(
    prefix="/invitations/api/v1",
    tags=["Invitations"],
    dependencies=[Depends(jwt_required)],
)


@router.post(
    "/",
    response_model=CreateInvitationOutput,
    status_code=201,
)
@limiter.limit("20/minute")
async def create_invitation(
    inviter_id: CurrentUserId,
    request: Request,
    data: CreateProjectInvitation,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
):
    token = await service.create_project_invitation(data, inviter_id)
    return CreateInvitationOutput(
        msg="Invitation created successfully.",
        token=token,
        accept_url=f"{router.prefix}/{token}/accept",
        reject_url=f"{router.prefix}/{token}/reject",
    )


@router.get(
    "/received",
    response_model=ListReceivedInvitationSchema,
    status_code=200,
    summary="Invitations waiting for the authenticated user",
)
@limiter.limit("20/minute")
async def get_received_invitations(
    user_id: CurrentUserId,
    request: Request,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
):
    return await service.get_received_invitations(user_id)


@router.delete(
    "/{invitation_id}", response_model=ProjectInvitationOutput, status_code=200
)
async def revoke_invitation(
    user_id: CurrentUserId,
    invitation_id: int,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
):
    await service.revoke_project_invitation(invitation_id, user_id)
    return ProjectInvitationOutput(msg="Invitation revoked successfully.")


@router.post("/{token}/accept", response_model=ProjectInvitationOutput, status_code=200)
@limiter.limit("20/minute")
async def accept_invitation(
    user_id: CurrentUserId,
    request: Request,
    token: str,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
):

    await service.respond_project_invitation(token, user_id, True)
    return ProjectInvitationOutput(msg="Invitation accepted successfully.")


@router.post("/{token}/reject", response_model=ProjectInvitationOutput, status_code=200)
@limiter.limit("20/minute")
async def reject_invitation(
    user_id: CurrentUserId,
    request: Request,
    token: str,
    service: IProjectInvitationService = Depends(get_project_invitation_service),
):

    await service.respond_project_invitation(token, user_id, False)
    return ProjectInvitationOutput(msg="Invitation rejected successfully.")
