"""
This tool allows agents to interact with the pygithub library
and operate on a GitHub repository.

To use this tool, you must first set as environment variables:
    GITHUB_API_TOKEN
    GITHUB_REPOSITORY -> format: {owner}/{repo}

TODO: remove below
Below is a sample script that uses the Github tool:

```python
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits.github.toolkit import GitHubToolkit
from langchain.llms import OpenAI
from langchain.utilities.github import GitHubAPIWrapper

llm = OpenAI(temperature=0)
github = GitHubAPIWrapper()
toolkit = GitHubToolkit.from_github_api_wrapper(github)
agent = initialize_agent(
    toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run(
    "{{Enter a prompt here to direct the agent}}"
)

```
"""
from typing import Optional, Type

from pydantic import Field

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from .github_wrapper import GitHubAPIWrapper
from asyncer import asyncify
from pydantic import BaseModel, Field
from datetime import datetime



class GetIssuesInput(BaseModel):
    ...

class GetIssuesTool(BaseTool):
    name = "get_issues"
    description = (
        "This tool will fetch a list of the repository's issues."
    )

    args_schema: Type[BaseModel] = GetIssuesInput

    api_wrapper: GitHubAPIWrapper = Field(default_factory=GitHubAPIWrapper)

    def _get_issues(self):
        return self.api_wrapper.get_issues()

    def _run(self, query: Optional[str] = None):
        return self._get_issues()

    # 这里不能用 position arg, 和 langchain 的实现有关
    async def _arun(self, query: Optional[str] = None):
        return await asyncify(self._run)(query=query)




class GetCommitsInput(BaseModel):
    author: Optional[str] = Field(None, description="author of this commit")
    since: Optional[str] = Field(None, description="the date and time of the commit since, e.g. 2023-01-01 00:00:00")
    until: Optional[str] = Field(None, description="the date and time of this commit until, e.g. 2023-01-01 02:01:00")

class GetCommitsTool(BaseTool):
    name = "get_commits"
    description = (
        "This tool will fetch a list of the repository's commits."
    )

    args_schema: Type[BaseModel] = GetCommitsInput

    api_wrapper: GitHubAPIWrapper = Field(default_factory=GitHubAPIWrapper)

    def _get_list(self, author: Optional[str] = None, since: Optional[str] = None, until: Optional[str] = None):
        _since = None
        try:
            _since = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                _since = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
            except Exception:
                ...
        
        _until = None
        try:
            _until = datetime.strptime(until, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                _until = datetime.strptime(until, "%Y-%m-%d")
            except Exception:
                ...

        return self.api_wrapper.get_commits(author=author, since=_since, until=_until)

    def _run(self, author: Optional[str] = None, since: Optional[str] = None, until: Optional[str] = None):
        return self._get_list(author=author, since=since, until=until)

    # 这里不能用 position arg, 和 langchain 的实现有关
    async def _arun(self, author: Optional[str] = None, since: Optional[str] = None, until: Optional[str] = None):
        return await asyncify(self._run)(author, since=since, until=until)





class GitHubAction(BaseTool):
    api_wrapper: GitHubAPIWrapper = Field(default_factory=GitHubAPIWrapper)
    mode: str
    name = ""
    description = ""

    def _run(
        self,
        instructions: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the GitHub API to run an operation."""
        return self.api_wrapper.run(self.mode, instructions)

    async def _arun(
        self,
        instructions: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return await asyncify(self._run)(instructions)
    
  


