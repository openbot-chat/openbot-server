from abc import ABC, abstractmethod 
from typing import List
from uuid import UUID
from models.agent_tool import AgentToolSchema



class AgentToolRetriever(ABC):
    @abstractmethod
    async def retrieve(self, agent_id: UUID, query: str)-> List[AgentToolSchema]:
        ...