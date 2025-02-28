from models.agent_tool import AgentToolSchema
from models.conversation import ConversationSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from langchain.tools.base import BaseTool
from langchain.agents.load_tools import load_huggingface_tool

from models.credentials import CredentialsSchemaBase


# 目前有 bug, RemoteTool not have outputs, transformers 返回和 langchain 不兼容，需要修复
class HuggingFaceAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        agent_tool_options = agent_tool.tool.options
        if not agent_tool_options:
            raise Exception("options not found")

        task_or_repo_id = str(agent_tool.options.get("task_or_repo_id", None))
        if not task_or_repo_id:
            raise Exception("credentials task_or_repo_id not set")

        model_repo_id = agent_tool.options.get("model_repo_id", None)

        token = str(credentials.data.get("token", None)) if credentials is not None else None

        tool = load_huggingface_tool(
            task_or_repo_id=task_or_repo_id,
            model_repo_id=model_repo_id,
            token=token,
            remote=True
        )

        return [
            tool,
        ]