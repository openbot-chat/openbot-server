from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from langchain.tools.base import BaseTool
from uuid import UUID
from core.tools.datasource.load_file_datasource import LoadFileDatasourceTool
from services.datasource_service import DatasourceService



class DatasourceAgentToolLoader(AgentToolLoader):
    def __init__(self, datasource_service: DatasourceService):
        self.datasource_service = datasource_service

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        datastore_id = agent_tool.options.get("datastore_id")
        if not datastore_id:
            raise Exception("datastore_id not config")

        return [
            LoadFileDatasourceTool(
                datastore_id = UUID(hex=datastore_id),
                datasource_service=self.datasource_service,
            ),
        ]