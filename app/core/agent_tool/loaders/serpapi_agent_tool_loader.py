from models.agent_tool import AgentToolSchema
from models.conversation import ConversationSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from langchain.tools.base import BaseTool

from models.credentials import CredentialsSchemaBase
from langchain.utilities.serpapi import SerpAPIWrapper
from slugify import slugify
from core.agent_tool.errors import AgentToolError


class SerpAPIAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        agent_tool_options = agent_tool.tool.options
        if not agent_tool_options:
            raise Exception("options not found")

        if not credentials:
            raise AgentToolError(agent_tool_id=agent_tool.id, description="credentials not found")

        serpapi_api_key = credentials.data.get("serpapi_api_key", None)
        if not serpapi_api_key:
            raise AgentToolError(
                agent_tool_id=agent_tool.id, 
                description="credentials serpapi_api_key not set",
                actions=[{
                    'name': 'edit_credentials',
                    'args': {
                        'agent_tool_id': agent_tool.id,
                        'params': 'serpapi_api_key',
                    }
                }]
            )

        serpapi = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)

        return [
            Tool(
                name=slugify(agent_tool.tool.name) or "Search",
                description=agent_tool.description or agent_tool.tool.description or "A search engine. Useful for when you need to answer questions about current events. Input should be a search query.",
                func=serpapi.run,
                coroutine=serpapi.arun,
            )
        ]