from abc import abstractmethod
from typing import Any
from models.agent import AgentSchema
from models.conversation import ConversationSchema
from .qa_agent_builder import QAAgentBuilder
from .chat_agent_builder import ChatAgentBuilder
from .openai_tools_agent_builder import OpenAIToolsAgentBuilder
from .openai_assistant_agent_builder import OpenAIAssistantAgentBuilder
from .sales_agent_builder import SalesAgentBuilder
# from .generative_agent_builder import GenerativeAgentBuilder
from .agent import Agent


builders = {
    "chat": ChatAgentBuilder,
    "qa": QAAgentBuilder,
    "sales": SalesAgentBuilder,
    "tools": OpenAIToolsAgentBuilder,
    "openai_assistant": OpenAIAssistantAgentBuilder,
    # "generative": GenerativeAgentBuilder,
}

class AgentBuilder:
    @classmethod
    async def build_agent(
        cls, 
        agent_type: str, 
        agent: AgentSchema,
        **kwargs: Any
    ) -> Agent:        
        if agent_type not in builders:
            agent_type = 'chat'

        if agent_type == 'qa':
            if agent.datastores is None or len(agent.datastores) == 0:
                agent_type = 'chat'

        if agent_type == 'tools':
            if (agent.tools is None or len(agent.tools) == 0) and (agent.datastores is None or len(agent.datastores)) == 0:
                agent_type = 'chat'

        builder = builders[agent_type]()
        return await builder.build(agent, **kwargs)