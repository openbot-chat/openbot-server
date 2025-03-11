from abc import ABC, abstractmethod
from typing import Dict, Any
from models.agent import AgentSchema



class AgentProvider(ABC):
    @abstractmethod
    async def create(self, agent: AgentSchema, options: Dict[str, Any]) -> Any:
        ...
    
    @abstractmethod
    async def delete(self, id: str, options: Dict[str, Any]) -> Any:
        ...

    @abstractmethod
    async def update(self, id: str, options: Dict[str, Any], updates: Dict[str, Any]) -> Any:
        ...