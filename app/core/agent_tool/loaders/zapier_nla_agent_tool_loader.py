from models.agent_tool import AgentToolSchema
from models.conversation import ConversationSchema
from .agent_tool_loader import AgentToolLoader
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain.utilities.openapi import OpenAPISpec
# from langchain.requests import Requests
from core.llm import LLMManager
from core.monkey_patching.tool import *
from slugify import slugify
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.agents import AgentType, initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.tools.base import BaseTool, Tool

from models.credentials import CredentialsSchemaBase


# 参考: https://github.com/homanp/superagent/blob/52b506ae7f7443796e8ad5985b8f2b7ba9b2ce7c/app/lib/tools.py#L20

class ZapierNLAAgentToolLoader(AgentToolLoader):
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        tool_config = agent_tool.tool.options
        if not tool_config:
            raise Exception("config not found")

        if not credentials:
            raise Exception("credentials not found")        

        llm = await self.llm_manager.load()

        zapier_nla_api_key = credentials.data["zapier_nla_api_key"]

        zapier = ZapierNLAWrapper(zapier_nla_api_key=zapier_nla_api_key)
        toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
        agent = initialize_agent(
            toolkit.get_tools(),
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

        return [
            Tool(
              name=slugify(agent_tool.tool.name),
              description=agent_tool.description or agent_tool.tool.description or "useful for when you need to do tasks.",
              func=agent.run,
              coroutine=asyncify(agent.run),
          )
        ]