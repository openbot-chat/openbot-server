from typing import List, Optional, Dict
from uuid import UUID
from fastapi import Depends, HTTPException, status
from repositories.sqlalchemy.agent_repository import AgentRepository
from repositories.sqlalchemy.agent_datastore_repository import AgentDatastoreRepository
from repositories.sqlalchemy.agent_tool_repository import AgentToolRepository
from api.dependencies.repository import make_repository
from models.agent import *
from models.agent_tool import *
from models.agent_datastore import *
from schemas.pagination import CursorPage, CursorParams
import logging
from core.agent_providers.factory import AgentProviderFactory
from api.dependencies.get_agent_provider_factory import get_agent_provider_factory
from .agent_provider_listener import AgentProviderListener
import pydash
from config import OPENAI_API_KEY, OPENAI_ORGANIZATION


class AgentService:
    def __init__(self, 
        repository: AgentRepository = Depends(make_repository(AgentRepository)),
        agent_datastore_repository: AgentDatastoreRepository = Depends(make_repository(AgentDatastoreRepository)),
        agent_tool_repository: AgentToolRepository = Depends(make_repository(AgentToolRepository)),
        agent_provider_factory: AgentProviderFactory = Depends(get_agent_provider_factory, use_cache=True),
        agent_provider_listener: AgentProviderListener = Depends(AgentProviderListener),
    ):
        self.repository = repository
        self.agent_tool_repository = agent_tool_repository
        self.agent_datastore_repository = agent_datastore_repository
        self.agent_provider_factory = agent_provider_factory
        self.agent_provider_listener = agent_provider_listener

    async def create(self, in_schema: CreateAgentSchema) -> AgentSchema:
        template = None
        if in_schema.template_id is not None:
            template = await self.repository.get_by_id(in_schema.template_id)
            
        if template is not None:
            in_schema.instructions = template.instructions
            in_schema.voice = template.voice
            in_schema.avatar = template.avatar

            if template.options is not None:
                extend_options: Dict[str, Any] = {
                    'provider': 'openai_assistant'
                }
                chain = template.options.get('chain')
                if chain is not None:
                    extend_options['chain'] = {
                        "type": chain.get("type", "tools"),
                    }

                in_schema.options = in_schema.options or {}
                in_schema.options.update(extend_options)
                in_schema.options = extend_options

        new_agent = await self.repository.create(in_schema)

        if template is not None:
            if template.tools is not None:
                for agent_tool in template.tools:
                    await self.agent_tool_repository.create(CreateAgentToolSchema(
                        agent_id=new_agent.id,
                        tool_id=agent_tool.tool_id,
                        name=agent_tool.name,
                        description=agent_tool.description,
                    ))

        agent_options = (new_agent.options or {}).copy()
        provider = pydash.get(agent_options, 'provider')
        provider_options = pydash.get(agent_options, provider, {})
        agent_config = await self.agent_provider_factory.create(new_agent, provider, provider_options)

        pydash.set_(agent_options, provider, { 
            'id': agent_config['id'],
        })
        pydash.set_(agent_options, 'provider', provider)

        updated_agent = await self.repository.update_by_id(new_agent.id, UpdateAgentSchema(options=agent_options))
        
        return updated_agent

    async def get_by_id(self, id: UUID) -> Optional[AgentSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_identifier(self, identifier: str) -> Optional[AgentSchema]:
        agent = await self.repository.get_by_identifier(identifier)
        if agent is not None:
            del agent.options
        return agent

    async def get_by_ids(self, ids: List[UUID]) -> List[AgentSchema]:
        return await self.repository.get_by_ids(ids)

    async def update_by_id(self, id: UUID, data: UpdateAgentSchema) -> AgentSchema:
        updated_agent = await self.repository.update_by_id(id, data)

        updates = {}
        if data.name is not None:
            updates['name'] = data.name
        if data.description is not None:
            updates['description'] = data.description
        if data.instructions is not None:
            updates['instructions'] = data.instructions

        agent_options = updated_agent.options or {}

        provider = agent_options.get('provider')
        if provider is not None:
            provider_options = agent_options.get(provider, {})
            provider_agent_id = provider_options.get("id")

            if len(updates) > 0 and provider_agent_id is not None:
                agent_config = await self.agent_provider_factory.update(provider, provider_agent_id, provider_options, updates)
                print(f'Agent of Provider({provider}) {agent_config["id"]} updated: ', agent_config)

        return updated_agent

    async def delete_by_id(self, id: UUID) -> AgentSchema:
        deleted_agent = await self.repository.delete_by_id(id)

        agent_options = deleted_agent.options or {}

        provider = agent_options.get('provider')
        if provider is not None:
            provider_options = agent_options.get(provider, {})
            provider_agent_id = provider_options.get("id")

            deleted = await self.agent_provider_factory.delete(provider, provider_agent_id, provider_options)
            print(f'Agent of Provider({provider}) {deleted["id"]} updated: ', deleted)

        return deleted_agent


    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[AgentSchema]:
        return await self.repository.paginate1(filter, params=params)
  
    async def count(self) -> int:
        return await self.repository.count()

    async def list_datastores(self, agent_id: UUID, params: Optional[CursorParams] = None) -> CursorPage[AgentDatastoreSchema]:
        return await self.agent_datastore_repository.paginate1(agent_id, params=params)

    async def bind_datastore(self, data: CreateAgentDatastoreSchema) -> AgentDatastoreSchema:        
        r = await self.agent_datastore_repository.create(data)
        await self.agent_provider_listener.on_update_agent_tools(data.agent_id)
        return r


    async def unbind_datastore(self, agent_id: UUID, datastore_id: UUID) -> AgentDatastoreSchema:
        r = await self.agent_datastore_repository.delete(agent_id, datastore_id)
        await self.agent_provider_listener.on_update_agent_tools(agent_id)
        return r


    async def update_provider(self, agent_id: UUID, provider: str, provider_options: Dict[str, Any]) -> bool:
        agent = await self.repository.get_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

        new_options = (agent.options or {}).copy()

        provider_options_exists =  new_options.get(provider)
        if provider_options_exists is not None and provider_options_exists.get('id') is not None:
            return True

        agent_config = await self.agent_provider_factory.create(agent, provider, provider_options)

        new_provider_options = provider_options.copy()
        new_provider_options['id'] = agent_config['id']
        new_options['chain'] = provider
        new_options[provider] = new_provider_options

        await self.repository.update_by_id(agent.id, UpdateAgentSchema(options=new_options))
        return True