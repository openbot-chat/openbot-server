
from typing import List
from typing import List
from ..agent_tool_retriever import AgentToolRetriever
from uuid import UUID
from vectorstore.datastore_manager import DatastoreManager
from vectorstore import Document, DocumentQuery, DocumentMetadataFilter
from config import (
    DEFAULT_QDRANT_OPTIONS
)
from services.agent_tool_service import AgentToolService
from models.agent_tool import AgentToolSchema



class VectorAgentToolRetriever(AgentToolRetriever):
    def __init__(self, agent_tool_service: AgentToolService):
        self.agent_tool_service = agent_tool_service

    async def retrieve(self, agent_id: UUID, query: str) -> List[AgentToolSchema]:
        vectorstore = DatastoreManager.get('qdrant', DEFAULT_QDRANT_OPTIONS)
        
        results = await vectorstore.query(
           'agent_tools',
          [
            DocumentQuery(
              query=query,
              top_k=4,
              filter=DocumentMetadataFilter(
                author=str(agent_id),
              )
            )
          ]
        )

        docs: List[Document] = []
        for result in results:
           for doc in result.results:
              docs.append(doc)

        agent_tool_ids = [UUID(hex=d.metadata.get('source_id')) for d in docs]

        agent_tools: List[AgentToolSchema]
        if len(agent_tool_ids) > 0:
            agent_tools = await self.agent_tool_service.get_by_ids(agent_tool_ids)
        else:
            agent_tools = []
        print('========== 找到 Agent tools: ', agent_tool_ids, agent_tools)

        return agent_tools
