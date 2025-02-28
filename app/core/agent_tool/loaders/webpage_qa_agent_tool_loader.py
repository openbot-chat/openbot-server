from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from core.llm.manager import LLMManager
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from langchain.tools.base import BaseTool
from langchain.chains.qa_with_sources.loading import (
    load_qa_with_sources_chain,
)
from core.tools.webpage_qa import WebpageQATool



class WebpageQAAgentToolLoader(AgentToolLoader):
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        # 由于 YouTubeSearchTool 的描述中给出了参数分割规则，如果直接返回 tool, gpt会把参数拆分成数组，导致调用出错. 所以用 agent 隔离一道

        llm = await self.llm_manager.load()
        return [
            WebpageQATool(
              qa_chain=load_qa_with_sources_chain(llm, chain_type="map_reduce", verbose=True),
            ),
        ]