from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List
from core.monkey_patching.tool import *
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from langchain.tools.base import BaseTool

from core.tools.github.github_wrapper import GitHubAPIWrapper
from core.tools.github.tool import GetCommitsTool, GetIssuesTool



class GithubAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        if not agent_tool.options:
            raise Exception("agent tool options not found")        
        
        if not credentials:
            raise Exception("credentials not found")

        github = GitHubAPIWrapper(
            github_app_id = credentials.data.get("app_id"),
            github_app_private_key = credentials.data.get("app_private_key"),
            github_repository = agent_tool.options.get("repository"),
            github_branch = agent_tool.options.get("branch"),
        )
        # toolkit = GitHubToolkit.from_github_api_wrapper(github)

        return [
            GetCommitsTool(
                api_wrapper=github,
            ),
            GetIssuesTool(
                api_wrapper=github,
            ),
        ]