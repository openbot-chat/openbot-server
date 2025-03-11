from langchain.tools.base import BaseTool
from .loaders.agent_tool_loader import AgentToolLoader
from typing import Dict, List, Optional
from models.agent_tool import AgentToolSchema
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema


class AgentToolLoaderManager:
    def __init__(self, loaders: Dict[str, AgentToolLoader]):
        self.loaders = loaders

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        loader = self.loaders.get(agent_tool.tool.type)
        if not loader:
            raise Exception(f'AgentTool type: {agent_tool.tool.type} not found')

        return await loader.load(agent_tool, credentials, conversation)