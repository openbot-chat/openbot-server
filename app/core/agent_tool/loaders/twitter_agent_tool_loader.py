from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from langchain.tools.base import BaseTool



class TwitterSearchAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:

        return []