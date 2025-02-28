from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List, Optional
from langchain.tools.base import BaseTool
from core.tools.vectorstore.tool import VectorstoreQueryTool
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from core.agent_tool.errors import AgentToolError
from vectorstore.datastore_manager import DatastoreManager
from db.session import async_session
from repositories.sqlalchemy.datastore_repository import DatastoreRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from uuid import UUID
import logging
from config import (
    DEFAULT_QDRANT_OPTIONS
)



class DatastoreAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        datastore_id = str(agent_tool.options.get("datastore_id"))

        max_results = agent_tool.options.get("max_results", 1)
        score_threshold = agent_tool.options.get("score_threshold", 0.6)

        async with async_session() as db_session:
            datastore_repository = DatastoreRepository(db_session)
            credentials_repository = CredentialsRepository(db_session)
            datastore = await datastore_repository.get_by_id(UUID(datastore_id))

            if not datastore:
                raise AgentToolError(agent_tool_id=agent_tool.id, description="credentials not found")

            # get datastore options
            options = None
            if datastore.options is not None:
                credentials_id = str(datastore.options.get('credentials_id'))
                credentials = await credentials_repository.get_by_id(UUID(hex=credentials_id))
                if credentials is not None:
                    options = credentials.data
                    logging.info(f"choose custom datastore, provider: {datastore.provider}, options: {options}")


        if options is None:
            options = DEFAULT_QDRANT_OPTIONS
            logging.info(f"choose default datastore, provider: {datastore.provider}, options: {options}")

        vectorstore = DatastoreManager.get(datastore.provider, options=options)

        return [
            VectorstoreQueryTool(
                name=str(agent_tool.tool.id),
                description=agent_tool.description or agent_tool.tool.description or (
                    "Use to query documents from datastore associated with a query string."
                ),
                return_direct=agent_tool.return_direct or agent_tool.tool.return_direct,
                vectorstore=vectorstore,
                collection_name=datastore.id.hex,
                max_results=max_results,
                score_threshold=score_threshold,
            )
        ]