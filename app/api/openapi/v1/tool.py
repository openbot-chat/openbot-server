
from fastapi import APIRouter, Depends, Request, Query, HTTPException
from models import ai_plugin as ai_plugin_schemas
from models.tool import *
from models.api import LoadPluginRequest
from services import ToolService, OrgService
from schemas.pagination import CursorPage, CursorParams
from security.auth0.auth import Auth0User
from typing import Optional

from api.dependencies.auth import get_auth_user
import requests


router = APIRouter()
from uuid import UUID




@router.post("", status_code=201, response_model=ToolSchema)
async def create_a_tool(
  tool: CreateToolSchema,
  tool_service: ToolService = Depends(ToolService),
  user: Auth0User = Depends(get_auth_user),
):
    return await tool_service.create(tool)

@router.get("/{tool_id}", response_model=Optional[ToolSchema])
async def retrieve_a_tool(
  tool_id: UUID,
  tool_service: ToolService = Depends(ToolService),
  user: Auth0User = Depends(get_auth_user),
):
  return await tool_service.get_by_id(tool_id)

@router.patch("/{tool_id}", response_model=ToolSchema)
async def update_a_tool(
  tool_id: UUID,
  data: UpdateToolSchema,
  tool_service: ToolService = Depends(ToolService),
  user: Auth0User = Depends(get_auth_user),
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
    request: Request,
    params: CursorParams = Depends(),
    filter: ToolFilter = Depends(),
    tool_service: ToolService = Depends(ToolService),
    org_service: OrgService = Depends(OrgService)
):
    """tools list"""
    if filter.org_id is not None:
        member = await org_service.get_member(UUID(hex=filter.org_id), request.state.api_key.user_id)
        if member is None:
            raise HTTPException(status_code=401, detail={'error': 'no permission'})

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


@router.post("/{tool_id}/run")
async def run_a_tool(
    tool_id: UUID,
    req: ToolRunRequest,
    tool_service: ToolService = Depends(ToolService),
):
    return await tool_service.run(tool_id, req)