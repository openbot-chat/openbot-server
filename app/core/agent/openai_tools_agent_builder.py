from typing import Any
from models.agent import AgentSchema
from .openai_tools_agent import OpenAIToolsAgent
from .agent import Agent



class OpenAIToolsAgentBuilder:
    async def build(
        self, 
        agent: AgentSchema,
        **kwargs: Any,
    ) -> Agent:
        return OpenAIToolsAgent(
            agent=agent,
            **kwargs,
        )