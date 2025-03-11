
from typing import Dict
from core.agent_providers.factory import AgentProviderFactory
from core.agent_providers.openai_assistant_provider import OpenAIAssistantProvider
from core.agent_providers.agent_provider import AgentProvider


def get_agent_provider_factory() -> AgentProviderFactory:
    providers: Dict[str, AgentProvider] = {
        "openai_assistant": OpenAIAssistantProvider(),
    }
    
    return AgentProviderFactory(providers)