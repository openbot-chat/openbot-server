from typing import Optional, List
from fastapi import APIRouter, Depends, Request, Body, HTTPException, UploadFile, File, Query
from schemas.pagination import CursorParams, CursorPage
from models.metafield import *
from services.metafield_service import MetafieldService
from uuid import UUID



router = APIRouter()

@router.post("", status_code=201, response_model=MetafieldSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_metafield(
    metafield: CreateMetafieldSchema,
    metafield_service: MetafieldService = Depends(MetafieldService),
):
    return await metafield_service.create(metafield)

@router.get("/{metafield_id}", response_model=Optional[MetafieldSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_metafield(
    metafield_id: UUID,
    metafield_service: MetafieldService = Depends(MetafieldService),
):
    metafield = await metafield_service.get_by_id(metafield_id)
    if not metafield:
        raise HTTPException(status_code=404, detail="Metafield not found")
    return metafield


@router.patch("/{metafield_id}", response_model=MetafieldSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_metafield(
    metafield_id: UUID,
    data: UpdateMetafieldSchema,
    metafield_service: MetafieldService = Depends(MetafieldService),
):
    return await metafield_service.update_by_id(metafield_id, data)

@router.delete("/{metafield_id}", status_code=204)
async def delete_a_metafield(
    metafield_id: UUID,
    metafield_service: MetafieldService = Depends(MetafieldService),
):
    await metafield_service.delete_by_id(metafield_id)

# 不能暴露这个方法出去, 没有办法做租户隔离
@router.get("", response_model=CursorPage[MetafieldSchema], response_model_exclude_unset=True)
async def list_metafields(
    filter: MetafieldFilter = Depends(None),
    params: CursorParams = Depends(),
    metafield_service: MetafieldService = Depends(MetafieldService),
):
    return await metafield_service.query(filter, params=params)