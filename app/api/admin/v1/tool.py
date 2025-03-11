from fastapi import APIRouter, Depends, Query
from models import ai_plugin as ai_plugin_schemas
from models.tool import *
from models.api import LoadPluginRequest
from services.tool_service import ToolService
from schemas.pagination import CursorPage, CursorParams
from typing import Optional
import requests
from api.dependencies.auth import get_org_id

router = APIRouter()
from uuid import UUID




@router.post("", status_code=201, response_model=ToolSchema)
async def create_a_tool(
    tool: CreateToolSchema,
    tool_service: ToolService = Depends(ToolService),
):
    return await tool_service.create(tool)

@router.get("/{tool_id}", response_model=Optional[ToolSchema])
async def retrieve_a_tool(
    tool_id: UUID,
    tool_service: ToolService = Depends(ToolService),
):
    return await tool_service.get_by_id(tool_id)

@router.patch("/{tool_id}", response_model=ToolSchema)
async def update_a_tool(
    tool_id: UUID,
    data: UpdateToolSchema,
    tool_service: ToolService = Depends(ToolService),
):
    return await tool_service.update_by_id(tool_id, data)

@router.delete("/{tool_id}", status_code=204)
async def delete_a_tool(
    tool_id: UUID,
    tool_service: ToolService = Depends(ToolService),
):
    return await tool_service.delete_by_id(tool_id)

@router.get("", response_model=CursorPage[ToolSchema])
async def list_tools(
    params: CursorParams = Depends(),
    filter: ToolFilter = Depends(),
    tool_service: ToolService = Depends(ToolService),
):
    """获取 tools 列表"""
    return await tool_service.paginate(filter, params)

@router.post("/ai-plugins/load")
async def load_a_plugin(
    req: LoadPluginRequest,
    tool_service: ToolService = Depends(ToolService),
):
    # need change to aiohttp
    response = requests.get(req.url)
    data = response.json()

    data['manifest_url'] = req.url

    ai_plugin = ai_plugin_schemas.CreateAIPluginSchema.parse_obj(data)
    tool = CreateToolSchema(
        name=ai_plugin.name_for_model,
        description=ai_plugin.description_for_model,
        type="ai_plugin",
        options=ai_plugin.dict(),
    )

    return await tool_service.create(tool)