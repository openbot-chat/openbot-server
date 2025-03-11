from typing import Any
from models.agent import AgentSchema
from .openai_assistant_agent import OpenAIAssistantAgent
from .agent import Agent



class OpenAIAssistantAgentBuilder:
    async def build(
        self, 
        agent: AgentSchema,
        **kwargs: Any,
    ) -> Agent:
        return OpenAIAssistantAgent(
            agent=agent,
            **kwargs,
        )