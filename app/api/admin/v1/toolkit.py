from fastapi import APIRouter, Depends, Query
from models.toolkit import *
from services.toolkit_service import ToolkitService
from schemas.pagination import CursorPage, CursorParams
from typing import Optional
router = APIRouter()
from uuid import UUID




@router.post("", status_code=201, response_model=ToolkitSchema)
async def create_a_toolkit(
    toolkit: CreateToolkitSchema,
    toolkit_service: ToolkitService = Depends(ToolkitService),
):
    return await toolkit_service.create(toolkit)

@router.get("/{toolkit_id}", response_model=Optional[ToolkitSchema])
async def retrieve_a_toolkit(
    toolkit_id: UUID,
    toolkit_service: ToolkitService = Depends(ToolkitService),
):
    return await toolkit_service.get_by_id(toolkit_id)

@router.patch("/{toolkit_id}", response_model=ToolkitSchema)
async def update_a_toolkit(
    toolkit_id: UUID,
    data: UpdateToolkitSchema,
    toolkit_service: ToolkitService = Depends(ToolkitService),
):
    return await toolkit_service.update_by_id(toolkit_id, data)

@router.delete("/{toolkit_id}", status_code=204)
async def delete_a_toolkit(
    toolkit_id: UUID,
    toolkit_service: ToolkitService = Depends(ToolkitService),
):
    return await toolkit_service.delete_by_id(toolkit_id)

@router.get("", response_model=CursorPage[ToolkitSchema])
async def list_toolkits(
    params: CursorParams = Depends(),
    org_id: str = Query(...),
    toolkit_service: ToolkitService = Depends(ToolkitService),
):
    """获取 toolkits 列表"""
    filter = {
        "org_id": org_id,
    }

    return await toolkit_service.query(filter, params)