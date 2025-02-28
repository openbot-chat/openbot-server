from models.agent_tool import AgentToolSchema
from models.conversation import ConversationSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from core.llm.manager import LLMManager
from models.credentials import CredentialsSchemaBase
from langchain.tools.base import BaseTool

from core.tools.youtube.youtube_search_tool import YouTubeSearchTool
from core.tools.youtube.youtube_transcribe_tool import YoutubeTranscribeTool



class YoutubeSearchAgentToolLoader(AgentToolLoader):
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        # 由于 YouTubeSearchTool 的描述中给出了参数分割规则，如果直接返回 tool, gpt会把参数拆分成数组，导致调用出错. 所以用 agent 隔离一道

        return [
            YouTubeSearchTool(),
            YoutubeTranscribeTool(llm_manager=self.llm_manager),
        ]