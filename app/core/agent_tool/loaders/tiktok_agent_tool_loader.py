from models.agent_tool import AgentToolSchema
from models.conversation import ConversationSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from models.credentials import CredentialsSchemaBase
from langchain.tools.base import BaseTool
from core.tools.tiktok.tiktok_search_tool import TiktokSearchTool



class TiktokAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        if not credentials:
            raise Exception("credentials not found")        

        client_key = credentials.data.get("client_key", None)
        if not client_key:
            raise Exception("tiktok client_key not set")            

        client_secret = credentials.data.get("client_secret", None)
        if not client_secret:
            raise Exception("tiktok client_secret not set")            

        return [
            TiktokSearchTool(
                credentials=credentials
            )
        ]