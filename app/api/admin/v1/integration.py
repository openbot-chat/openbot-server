
from fastapi import APIRouter, Depends, Query
from models import ai_plugin as ai_plugin_schemas
from models.integration import *
from models.api import LoadPluginRequest
from services.integration_service import IntegrationService
from schemas.pagination import CursorPage, CursorParams
from typing import Optional, List
import requests


router = APIRouter()
from uuid import UUID



@router.post("", status_code=201, response_model=IntegrationSchema)
async def create_a_integration(
    integration: CreateIntegrationSchema,
    integration_service: IntegrationService = Depends(IntegrationService),
):
    return await integration_service.create(integration)

@router.get("/by-identifier/{identifier}", response_model=Optional[IntegrationSchema])
async def retrieve_a_integration_by_identifier(
    identifier: str,
    integration_service: IntegrationService = Depends(IntegrationService),
):
    return await integration_service.get_by_identifier(identifier)

@router.get("/{integration_id}", response_model=Optional[IntegrationSchema])
async def retrieve_a_integration(
    integration_id: UUID,
    integration_service: IntegrationService = Depends(IntegrationService),
):
    return await integration_service.get_by_id(integration_id)

@router.patch("/{integration_id}", response_model=IntegrationSchema)
async def update_a_integration(
    integration_id: UUID,
    data: UpdateIntegrationSchema,
    integration_service: IntegrationService = Depends(IntegrationService),
):
    return await integration_service.update_by_id(integration_id, data)

@router.delete("/{integration_id}", status_code=204)
async def delete_a_integration(
    integration_id: UUID,
    integration_service: IntegrationService = Depends(IntegrationService),
):
    return await integration_service.delete_by_id(integration_id)

@router.get("", response_model=CursorPage[IntegrationSchema])
async def list_integrations(
    catalog: Optional[List[str]] = Query(None),
    collection: Optional[str] = Query(None),
    params: CursorParams = Depends(),
    integration_service: IntegrationService = Depends(IntegrationService),
):
    """获取 integrations 列表"""
    filter = {}
    if catalog:
        filter["catalog"] = catalog
    
    if collection:
        filter["collection"] = collection

    return await integration_service.paginate(filter, params)

@router.post("/ai-plugins/load")
async def load_a_plugin(
    req: LoadPluginRequest,
    integration_service: IntegrationService = Depends(IntegrationService),
):
    # need change to aiohttp
    response = requests.get(req.url)
    data = response.json()

    data['manifest_url'] = req.url

    ai_plugin = ai_plugin_schemas.CreateAIPluginSchema.parse_obj(data)
    integration = CreateIntegrationSchema(
        name=ai_plugin.name_for_human,
        identifier=UUID().hex,
        catalog="ai_plugin",
        options=ai_plugin.dict(),
    )

    return await integration_service.create(integration)
