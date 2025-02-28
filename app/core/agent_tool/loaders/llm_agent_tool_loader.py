from models.agent_tool import AgentToolSchema
from models.conversation import ConversationSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from langchain.tools.base import BaseTool

from models.credentials import CredentialsSchemaBase
from core.agent_tool.errors import AgentToolError
from core.llm.manager import LLMManager
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage



class LLMAgentToolLoader(AgentToolLoader):
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        agent_tool_options = agent_tool.tool.options
        if not agent_tool_options:
            raise Exception("options not found")

        messages: List[BaseMessage] = []
        raw_messages = agent_tool.options.get('messages', [])
        for raw_message in raw_messages:
            _type = raw_message['type']
            message: Optional[BaseMessage] = None
            if _type == 'system':
                  message = SystemMessage(**raw_message)
            elif _type == 'human':
                 message = HumanMessage(**raw_message)
            elif _type == 'ai':
                 message = AIMessage(**raw_message)
            
            if message is not None:
                messages.append(message)

        if not credentials:
            raise AgentToolError(agent_tool_id=agent_tool.id, description="credentials not found")


        llm = await self.llm_manager.load(credentials, {
            "_type": credentials.type,
            "verbose": True,
        })

        def run(query: str):
            messages.append(HumanMessage(
                content=query,
            ))
            return llm.invoke(messages)

        async def arun(query: str):
            messages.append(HumanMessage(
                content=query,
            ))
            return await llm.ainvoke(query)

        return [
            Tool(
                name=str(agent_tool.tool_id),
                description=agent_tool.description or agent_tool.tool.description,
                func=run,
                coroutine=arun,
            )
        ]