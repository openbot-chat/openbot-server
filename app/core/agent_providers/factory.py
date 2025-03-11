from typing import Dict, Any
from .agent_provider import AgentProvider
from core.errors import ProviderNotExistsError
from models.agent import AgentSchema



class AgentProviderFactory:
    def __init__(self, providers: Dict[str, AgentProvider]):
        self.providers = providers
    
    async def create(self, agent: AgentSchema, provider: str, options: Dict[str, Any]) -> Any:
        p = self.providers.get(provider)
        if not p:
            raise ProviderNotExistsError(provider)

        return await p.create(agent, options)

    async def delete(self, provider: str, id: str, options: Dict[str, Any]) -> Any:
        p = self.providers.get(provider)
        if not p:
            raise ProviderNotExistsError(provider)

        return await p.delete(id, options)
    
    async def update(self, provider: str, id: str, options: Dict[str, Any], updates: Dict[str, Any]) -> Any:
        p = self.providers.get(provider)
        if not p:
            raise ProviderNotExistsError(provider)

        return await p.update(id, options, updates)