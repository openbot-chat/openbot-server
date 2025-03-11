from typing import Any
from models.agent import AgentSchema
from .sales_agent import SalesAgent
from services.prompt_service import PromptService
from services.conversation_service import ConversationService
from services.credentials_service import CredentialsService
from core.llm.manager import LLMManager
from .agent import Agent

from langchain.memory.chat_memory import BaseMemory


class SalesAgentBuilder:
    async def build(
        self, 
        agent: AgentSchema,
        **kwargs: Any,
    ) -> Agent:
        return SalesAgent(
            agent=agent,
            **kwargs,
        )