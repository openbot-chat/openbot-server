from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from core.llm.manager import LLMManager

from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from langchain.tools.base import BaseTool
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.agents import create_sql_agent



class SQLDatabaseAgentToolLoader(AgentToolLoader):
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        tool_options = agent_tool.tool.options
        if not tool_options:
            raise Exception("options not found")

        if not credentials:
            raise Exception("credentials not found")        

        uri = credentials.data.get("uri", None)
        if not uri:
            raise Exception("credentials uri not set")            

        db = SQLDatabase.from_uri(uri)

        llm = await self.llm_manager.load()

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )


        return [
            Tool(
                name=str(agent_tool.tool.id),
                description=agent_tool.description or agent_tool.tool.description,
                func=agent_executor.run,
            )
        ]