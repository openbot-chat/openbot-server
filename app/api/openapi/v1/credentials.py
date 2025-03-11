from fastapi import APIRouter, Depends, Request, HTTPException
from models.credentials import *
from services import (
    CredentialsService,
    OrgService,
)
from schemas.pagination import CursorParams, CursorPage
from security.auth0.auth import Auth0User
from api.dependencies.auth import get_auth_user
from api.context import get_global_org_id
from api.admin.v1.dto.credentials import *


router = APIRouter()
from uuid import UUID



@router.post("", status_code=201, response_model=CredentialsSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_credentials(
    data: CreateCredentialsSchema,
    credentials_service: CredentialsService = Depends(CredentialsService),
    org_service: OrgService = Depends(OrgService),
    user: Auth0User = Depends(get_auth_user),
):
    await org_service.get_member(data.org_id, user.id)

    return await credentials_service.create(data)

@router.get("/{credentials_id}", response_model=CredentialsSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_credentials(
    credentials_id: UUID,
    credentials_service: CredentialsService = Depends(CredentialsService),
    user: Auth0User = Depends(get_auth_user),
):
    credentials = await credentials_service.get_by_id(credentials_id)
    if not credentials:
        raise HTTPException(status_code=404, detail={'error': 'credentials not found'})

    if credentials.org_id != get_global_org_id():
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    return credentials


@router.patch("/{credentials_id}", response_model=CredentialsSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_credentials(
    credentials_id: UUID,
    data: UpdateCredentialsSchema,
    credentials_service: CredentialsService = Depends(CredentialsService),
    user: Auth0User = Depends(get_auth_user),
):
    credentials = await credentials_service.get_by_id(credentials_id)
    if not credentials:
        raise HTTPException(status_code=404, detail={'error': 'credentials not found'})

    if credentials.org_id != get_global_org_id():
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    return await credentials_service.update_by_id(credentials_id, data)


@router.delete("/{credentials_id}", status_code=204)
async def delete_a_credentials(
    credentials_id: UUID,
    credentials_service: CredentialsService = Depends(CredentialsService),
):
    credentials = await credentials_service.get_by_id(credentials_id)
    if not credentials:
        raise HTTPException(status_code=404, detail={'error': 'credentials not found'})

    if credentials.org_id != get_global_org_id():
        raise HTTPException(status_code=401, detail={'error': 'no permission'})

    await credentials_service.delete_by_id(credentials_id)

@router.get("", response_model=CursorPage[CredentialsSchema], response_model_exclude_unset=True)
async def list_credentials(
    request: Request,
    filter: CredentialsFilter = Depends(),
    params: CursorParams = Depends(),
    credentials_service: CredentialsService = Depends(CredentialsService),
    org_service: OrgService = Depends(OrgService),
):
    """credentials list"""
    if filter.org_id is not None:
        member = await org_service.get_member(UUID(hex=filter.org_id), request.state.api_key.user_id)
        if member is None:
            raise HTTPException(status_code=401, detail={'error': 'no permission'})

    return await credentials_service.paginate(filter.dict(exclude_unset=True, exclude_none=True), params=params)