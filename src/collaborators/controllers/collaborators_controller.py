from fastapi import APIRouter, Depends, Request

from core.security.jwt_manager import CurrentUserId
from shared.extensions import limiter

from ..dependencies import get_collaborators_service
from ..schemas.collaborators_schema import (
    CollaboratorsOutputSchema,
    ListDetailCollaboratorsSchema,
    UpdateCollaboratorsSchema,
)
from ..interfaces import ICollaboratorService

router = APIRouter(prefix="/collaborators/api/v1", tags=["Collaborators"])
project_collaborators_router = APIRouter(prefix="/projects/api/v1", tags=["Collaborators"])


@project_collaborators_router.get(
    "/{project_id}/collaborators",
    response_model=ListDetailCollaboratorsSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def get_collaborators(
    user_id: CurrentUserId,
    request: Request,
    project_id: int,
    service: ICollaboratorService = Depends(get_collaborators_service),
):
    return await service.get_collaborators(project_id, user_id)


@router.delete(
    "/{collaborator_id}",
    response_model=CollaboratorsOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def remove_collaborator(
    user_id: CurrentUserId,
    request: Request,
    collaborator_id: int,
    service: ICollaboratorService = Depends(get_collaborators_service),
):

    await service.remove_collaborator(collaborator_id, user_id)
    return CollaboratorsOutputSchema(msg="Collaborator removed")


@router.patch(
    "/{collaborator_id}",
    response_model=CollaboratorsOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def change_role_collaborator(
    user_id: CurrentUserId,
    request: Request,
    collaborator_id: int,
    data: UpdateCollaboratorsSchema,
    service: ICollaboratorService = Depends(get_collaborators_service),
):
    await service.change_role_collaborator(collaborator_id, data, user_id)
    return CollaboratorsOutputSchema(msg="Collaborator updated")