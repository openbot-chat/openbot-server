
from typing import List
from typing import List
from ..agent_tool_retriever import AgentToolRetriever
from uuid import UUID
from services.agent_tool_service import AgentToolService
from models.agent_tool import AgentToolSchema, AgentToolFilter
from schemas.pagination import CursorParams



class DatabaseAgentToolRetriever(AgentToolRetriever):
    def __init__(self, agent_tool_service: AgentToolService):
        self.agent_tool_service = agent_tool_service

    async def retrieve(self, agent_id: UUID, query: str) -> List[AgentToolSchema]:
        page = await self.agent_tool_service.paginate(
            AgentToolFilter(
                agent_id=agent_id,
            ), 
            CursorParams(
                size=100
            )
        )

        return list(page.items)