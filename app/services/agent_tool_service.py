from uuid import UUID
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from repositories.sqlalchemy.agent_tool_repository import AgentToolRepository
from repositories.sqlalchemy.agent_repository import AgentRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from api.dependencies.repository import make_repository
from models.agent_tool import *
from schemas.pagination import CursorParams, CursorPage
from models.api import DocumentMetadataFilter
from vectorstore.datastore_manager import DatastoreManager

from .agent_provider_listener import AgentProviderListener
from config import (
    DEFAULT_QDRANT_OPTIONS
)

class AgentToolService:
    def __init__(
        self, 
        repository: AgentToolRepository = Depends(make_repository(AgentToolRepository)),
        agent_repository: AgentRepository = Depends(make_repository(AgentRepository)),
        credentials_repository: CredentialsRepository = Depends(make_repository(CredentialsRepository)),
        agent_provider_listener: AgentProviderListener = Depends(AgentProviderListener),
    ):
        self.repository = repository
        self.agent_repository = agent_repository
        self.credentials_repository = credentials_repository
        self.agent_provider_listener = agent_provider_listener

    async def create(self, in_schema: CreateAgentToolSchema) -> AgentToolSchema:
        agent_tool = await self.repository.create(in_schema)
        
        # TODO 触发事件，更新 assistant update tools
        await self.agent_provider_listener.on_update_agent_tools(agent_tool.agent_id)

        return agent_tool

    async def get_by_id(self, id: UUID) -> Optional[AgentToolSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_ids(self, ids: List[UUID]) -> List[AgentToolSchema]:
        return await self.repository.get_by_ids(ids)

    async def update_by_id(self, id: UUID, data: UpdateAgentToolSchema) -> AgentToolSchema:
        updated =  await self.repository.update_by_id(id, data)
        await self.agent_provider_listener.on_update_agent_tools(updated.agent_id)
        return updated

    async def delete_one(self, agent_id: UUID, id: UUID) -> AgentToolSchema:
        agent_tool = await self.get_by_id(id)
        if agent_tool is None:
            raise HTTPException(status_code=404, detail="AgentTool not found")
    
        if agent_tool.agent_id != agent_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AgentTool not found by agent")

        collection_name = 'agent_tools'
        vectorstore = DatastoreManager.get('qdrant', DEFAULT_QDRANT_OPTIONS)
    
        success = await vectorstore.delete(
            collection_name,
            filter = DocumentMetadataFilter(
                source_id=str(id),
                author=str(agent_id),
            ),
        )

        
        deleted = await self.repository.delete_by_id(id)

        await self.agent_provider_listener.on_update_agent_tools(agent_id)

        return deleted

    async def paginate(self, filter: AgentToolFilter, params: CursorParams) -> CursorPage[AgentToolSchema]:
        return await self.repository.paginate1(filter=filter, params=params)