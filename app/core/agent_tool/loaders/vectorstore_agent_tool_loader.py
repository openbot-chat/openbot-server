from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List, Optional
from langchain.tools.base import BaseTool
from core.tools.vectorstore.tool import VectorstoreQueryTool, VectorstoreUpsertTool
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from slugify import slugify
from core.agent_tool.errors import AgentToolError
from vectorstore.datastore_manager import DatastoreManager


class VectorstoreAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        if not credentials:
            raise AgentToolError(agent_tool_id=agent_tool.id, description="credentials not found")

        provider = str(agent_tool.options.get("provider", "qdrant"))

        collection_name = str(agent_tool.options.get("collection_name"))

        vectorstore = DatastoreManager.get(provider, options=credentials.data)

        await vectorstore.create_collection(collection_name)

        return [
            VectorstoreQueryTool(
                description=agent_tool.description or agent_tool.tool.description or (
                    "query documents from vectorstore associated with a query string."
                    "You should enter query as query string."
                    "You can enter top_k as the maximum number of results."
                ),
                vectorstore=vectorstore,
                collection_name=collection_name,
            ),
            VectorstoreUpsertTool(
                vectorstore=vectorstore,
                collection_name=collection_name,
            )
        ]