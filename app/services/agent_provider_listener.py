from typing import List, Any
from langchain.agents.tools import BaseTool
from langchain.tools.render import format_tool_to_openai_tool
from models.credentials import CredentialsSchemaBase
from core.agent_tool.agent_tool_loader_manager import AgentToolLoaderManager
from api.dependencies.agent_tool_loader_manager import get_agent_tool_loader_manager
from fastapi import Depends        
from uuid import UUID
from api.dependencies.repository import make_repository
from repositories.sqlalchemy.agent_repository import AgentRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from repositories.sqlalchemy.agent_tool_repository import AgentToolRepository
from repositories.sqlalchemy.agent_datastore_repository import AgentDatastoreRepository
from models.agent_tool import *
from schemas.pagination import CursorParams
import openai
import logging


class AgentProviderListener:
    def __init__(
        self,
        agent_tool_loader_manager: AgentToolLoaderManager = Depends(get_agent_tool_loader_manager),
        credentials_repository: CredentialsRepository = Depends(make_repository(CredentialsRepository)),
        agent_repository: AgentRepository = Depends(make_repository(AgentRepository)),
        agent_tool_repository: AgentToolRepository = Depends(make_repository(AgentToolRepository)),
        agent_datastore_repository: AgentDatastoreRepository = Depends(make_repository(AgentDatastoreRepository)),
    ):
        self.agent_tool_loader_manager = agent_tool_loader_manager
        self.credentials_repository = credentials_repository
        self.agent_repository = agent_repository
        self.agent_tool_repository = agent_tool_repository
        self.agent_datastore_repository = agent_datastore_repository


    async def on_update_agent_tools(self, agent_id: UUID):
        agent = await self.agent_repository.get_by_id(agent_id)
        if not agent:
            return

        options = agent.options or {}
        provider = options.get('provider')

        if not provider:
            return 

        if provider != 'openai_assistant':
            return

        provider_options = options.get(provider, {})

        assitant_id = str(provider_options['id'])
        if not assitant_id:
            return



        tools: List[BaseTool] = []

        datastore_page = await self.agent_datastore_repository.paginate1(
            agent_id,
            CursorParams(
                size=100
            )
        )
        agent_datastores = list(datastore_page.items)

        logging.debug(f'找到可以使用的 agent datastores: ', agent_datastores)


        agent_tools: List[AgentToolSchema] = []

        # 把 datastore 转换成 datastore tool
        for agent_datastore in agent_datastores:
            datastore = agent_datastore.datastore
            if not datastore:
                continue
            
            agent_tool = AgentToolSchema(
                id=agent_datastore.id,
                tool_id=datastore.id,
                agent_id=agent_id,
                name=datastore.name_for_model,
                description=datastore.description_for_model,
                tool=ToolSchema(
                    id=datastore.id,
                    name=datastore.name_for_model,
                    description=datastore.description_for_model,
                    created_at=datastore.created_at,
                    updated_at=datastore.updated_at,
                    type='datastore',
                    options={},
                ),
                options={
                    "datastore_id": str(datastore.id),
                    "max_results": 4,
                    # "score_threshold": 0.5,
                },
                created_at=agent_datastore.created_at,
                updated_at=agent_datastore.updated_at,
            )

            agent_tools.append(agent_tool)


        tool_page = await self.agent_tool_repository.paginate1(
            AgentToolFilter(
                agent_id=agent_id,
            ), 
            CursorParams(
                size=100
            )
        )

        agent_tools.extend(tool_page.items)

        print(f'找到可以使用的 agent tools: {len(agent_tools)}')


        for agent_tool in agent_tools:
            credentials: Optional[CredentialsSchemaBase] = None
            credentials_id = agent_tool.options.get("credentials_id")
            if credentials_id is not None:
                credentials = await self.credentials_repository.get_by_id(credentials_id)
                print("credentials_id: ", credentials_id, credentials)


            agent_tool_instances = await self.agent_tool_loader_manager.load(agent_tool, credentials)
            tools += agent_tool_instances

        openai_tools: List = []
        for tool in tools:
            oai_tool = (
                tool if isinstance(tool, dict) else format_tool_to_openai_tool(tool)
            )
            openai_tools.append(oai_tool)

        
        client = openai.AsyncOpenAI()
        assistant = await client.beta.assistants.update(
            assistant_id=assitant_id,
            tools=openai_tools,
        )

        print('assistant tools updated: ', assistant)