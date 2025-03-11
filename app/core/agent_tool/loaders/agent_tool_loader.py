from abc import ABC, abstractmethod
from langchain.tools.base import BaseTool
from typing import List, Optional
from models.agent_tool import AgentToolSchema
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema


class AgentToolLoader(ABC):
    @abstractmethod
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        ...