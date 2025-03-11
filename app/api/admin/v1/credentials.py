from fastapi import APIRouter, Depends, HTTPException
from models.credentials import *
from services import CredentialsService
from schemas.pagination import CursorParams, CursorPage
from .dto.credentials import *



router = APIRouter()
from uuid import UUID



@router.post("", status_code=201, response_model=CredentialsSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_credentials(
    data: CreateCredentialsSchema,
    credentials_service: CredentialsService = Depends(CredentialsService),
):
    return await credentials_service.create(data)

@router.get("/{credentials_id}", response_model=CredentialsSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_credentials(
    credentials_id: UUID,
    credentials_service: CredentialsService = Depends(CredentialsService),
):
    credentials = await credentials_service.get_by_id(credentials_id)
    if not credentials:
        raise HTTPException(status_code=404, detail={'error': 'credentials not found'})

    return credentials


@router.patch("/{credentials_id}", response_model=CredentialsSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_credentials(
    credentials_id: UUID,
    data: UpdateCredentialsSchema,
    credentials_service: CredentialsService = Depends(CredentialsService),
):
    credentials = await credentials_service.get_by_id(credentials_id)
    if not credentials:
        raise HTTPException(status_code=404, detail={'error': 'credentials not found'})

    return await credentials_service.update_by_id(credentials_id, data)


@router.delete("/{credentials_id}", status_code=204)
async def delete_a_credentials(
    credentials_id: UUID,
    credentials_service: CredentialsService = Depends(CredentialsService),
):
    credentials = await credentials_service.get_by_id(credentials_id)
    if not credentials:
        raise HTTPException(status_code=404, detail={'error': 'credentials not found'})

    await credentials_service.delete_by_id(credentials_id)

@router.get("", response_model=CursorPage[CredentialsSchema], response_model_exclude_unset=True)
async def list_credentials(
    filter: CredentialsFilter = Depends(),
    params: CursorParams = Depends(),
    credentials_service: CredentialsService = Depends(CredentialsService),
):
    """获取 credentials 列表"""
    return await credentials_service.paginate(filter.dict(exclude_unset=True, exclude_none=True), params=params)