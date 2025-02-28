from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from langchain.tools.base import BaseTool
from langchain.agents.agent_toolkits import GmailToolkit
from core.tools.gmail.utils import build_resource_service, get_gmail_credentials



class GmailAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        # 由于 YouTubeSearchTool 的描述中给出了参数分割规则，如果直接返回 tool, gpt会把参数拆分成数组，导致调用出错. 所以用 agent 隔离一道
        if not credentials:
            raise Exception("credentials not found")        

        info = credentials.data.get("info")

        google_credentials = get_gmail_credentials(
            info=info,
            scopes=["https://mail.google.com/"],
        )

        api_resource = build_resource_service(credentials=google_credentials)
        toolkit = GmailToolkit(api_resource=api_resource)

        return toolkit.get_tools()