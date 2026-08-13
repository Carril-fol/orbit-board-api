from fastapi import APIRouter, Depends, Request
from fastapi_cache.decorator import cache

from core.security.jwt_manager import jwt_required
from shared.extensions import limiter

from ..dependencies import get_collaborators_service
from ..schemas.collaborators_schema import (
    CollaboratorsOutputSchema,
    ListDetailCollaboratorsSchema,
    UpdateCollaboratorsSchema,
)
from ..interfaces import ICollaboratorService

router = APIRouter(prefix="/collaborators/api/v1", tags=["Collaborators"])


@router.get(
    "/get/{project_id}",
    response_model=ListDetailCollaboratorsSchema,
    status_code=200,
)
@cache(expire=30)
@limiter.limit("10/minute")
async def get_collaborators(
    request: Request,
    project_id: int,
    service: ICollaboratorService = Depends(get_collaborators_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    return await service.get_collaborators(project_id, user_id)


@router.delete(
    "/delete/{id_collaborator}",
    response_model=CollaboratorsOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def remove_collaborator(
    request: Request,
    id_collaborator: int,
    service: ICollaboratorService = Depends(get_collaborators_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]

    await service.remove_collaborator(id_collaborator, user_id)
    return CollaboratorsOutputSchema(msg="Collaborator removed")


@router.put(
    "/update-role/{collaborator_id}",
    response_model=CollaboratorsOutputSchema,
    status_code=200,
)
@limiter.limit("10/minute")
async def change_role_collaborator(
    request: Request,
    collaborator_id: int,
    data: UpdateCollaboratorsSchema,
    service: ICollaboratorService = Depends(get_collaborators_service),
    _payload: dict = Depends(jwt_required),
):
    user_id = _payload["sub"]
    await service.change_role_collaborator(collaborator_id, data, user_id)
    return CollaboratorsOutputSchema(msg="Collaborator updated")