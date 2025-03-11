
from fastapi import APIRouter, Depends
from typing import Optional
from models import api_key as api_key_schemas
from services.api_key_service import ApiKeyService
from schemas.pagination import CursorPage, CursorParams


router = APIRouter()
from uuid import UUID

@router.post("", status_code=201, response_model=api_key_schemas.ApiKeySchema)
async def create_a_api_key(
  api_key: api_key_schemas.CreateApiKeySchema,
  api_key_service: ApiKeyService = Depends(ApiKeyService),
):
  result = await api_key_service.create(api_key)
  return result

@router.get("/{api_key_id}", response_model=api_key_schemas.ApiKeySchema)
async def retrieve_a_api_key(
  api_key_id: UUID,
  api_key_service: ApiKeyService = Depends(ApiKeyService),
):
  return await api_key_service.get_by_id(api_key_id)

@router.patch("/{api_key_id}", response_model=api_key_schemas.ApiKeySchema)
async def update_a_api_key(
  api_key_id: UUID,
  data: api_key_schemas.UpdateApiKeySchema,
  api_key_service: ApiKeyService = Depends(ApiKeyService),
):
  return await api_key_service.update_by_id(api_key_id, data)

@router.delete("/{api_key_id}", status_code=204)
async def delete_a_api_key(
  api_key_id: UUID,
  api_key_service: ApiKeyService = Depends(ApiKeyService),
):
  return await api_key_service.delete_by_id(api_key_id)

@router.get("", response_model=CursorPage[api_key_schemas.ApiKeySchema])
async def list_api_keys(
  params: Optional[CursorParams] = Depends(),
  api_key_service: ApiKeyService = Depends(ApiKeyService),
):
  """获取 api_keys 列表"""
  return await api_key_service.paginate({}, params=params)
