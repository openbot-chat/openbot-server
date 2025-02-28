
from fastapi import APIRouter, Depends, Query
from typing import Optional
from models.api_key import *
from services.api_key_service import ApiKeyService
from schemas.pagination import CursorPage, CursorParams


router = APIRouter()
from uuid import UUID

@router.post("", status_code=201, response_model=ApiKeySchema)
async def create_a_api_key(
    api_key: CreateApiKeySchema,
    api_key_service: ApiKeyService = Depends(ApiKeyService),
):
    result = await api_key_service.create(api_key)
    return result

@router.get("/{api_key_id}", response_model=Optional[ApiKeySchema])
async def retrieve_a_api_key(
    api_key_id: UUID,
    api_key_service: ApiKeyService = Depends(ApiKeyService),
):
    return await api_key_service.get_by_id(api_key_id)

@router.patch("/{api_key_id}", response_model=ApiKeySchema)
async def update_a_api_key(
    api_key_id: UUID,
    data: UpdateApiKeySchema,
    api_key_service: ApiKeyService = Depends(ApiKeyService),
):
    return await api_key_service.update_by_id(api_key_id, data)

@router.delete("/{api_key_id}", status_code=204)
async def delete_a_api_key(
    api_key_id: UUID,
    api_key_service: ApiKeyService = Depends(ApiKeyService),
):
    return await api_key_service.delete_by_id(api_key_id)

@router.get("", response_model=CursorPage[ApiKeySchema])
async def list_api_keys(
    user_id: str = Query(),
    params: CursorParams = Depends(),
    api_key_service: ApiKeyService = Depends(ApiKeyService),
):
    """获取 api_keys 列表"""
    filter = { "user_id": user_id }
    return await api_key_service.paginate(filter, params=params)
