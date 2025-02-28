from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import Depends
from repositories.sqlalchemy.integration_repository import IntegrationRepository
from repositories.sqlalchemy.tool_repository import ToolRepository
from api.dependencies.repository import make_repository
from models import integration as integration_schemas
from schemas.pagination import CursorParams, CursorPage



class IntegrationService:
    def __init__(
        self, 
        repository: IntegrationRepository = Depends(make_repository(IntegrationRepository)),
        tool_repository: ToolRepository = Depends(make_repository(ToolRepository))
    ):
        self.repository = repository
        self.tool_repository = tool_repository


  
    async def create(self, in_schema: integration_schemas.CreateIntegrationSchema) -> integration_schemas.IntegrationSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[integration_schemas.IntegrationSchema]:
        integration = await self.repository.get_by_id(id)
        if integration is not None:
            ref_id = str(integration.options.get("id"))
            if integration.catalog == "tool": 
                tool = await self.tool_repository.get_by_id(UUID(hex=ref_id))
                integration.options["tool"] = tool
        return integration

    async def get_by_identifier(self, identifier: str) -> Optional[integration_schemas.IntegrationSchema]:
        integration = await self.repository.get_by_identifier(identifier)
        if integration is not None:
            ref_id = str(integration.options.get("id"))
            if integration.catalog == "tool": 
                tool = await self.tool_repository.get_by_id(UUID(hex=ref_id))
                integration.options["tool"] = tool
        return integration

    async def update_by_id(self, id: UUID, data: integration_schemas.UpdateIntegrationSchema) -> integration_schemas.IntegrationSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> integration_schemas.IntegrationSchema:
        return await self.repository.delete_by_id(id)

    async def get_by_ids(self, ids: List[UUID]) -> List[integration_schemas.IntegrationSchema]:
        return await self.repository.get_by_ids(ids)

    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams]) -> CursorPage[integration_schemas.IntegrationSchema]:
        return await self.repository.paginate1(filter, params=params)