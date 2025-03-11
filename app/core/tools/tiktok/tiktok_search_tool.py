from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from models.credentials import CredentialsSchemaBase
from core.credentials.credentilas_helper import CredentialsHelper
from asyncer import runnify



SEARCH_URL = "https://open.tiktokapis.com/v2/research/video/query/"

class TiktokSearchInput(BaseModel):
    query: str = Field(description="Query string", default="hot video")
    max_count: int = Field(description="The number of videos in response. Default is 4, max is 10.", default=4, max=10)


class TiktokSearchTool(BaseTool):
    """Tool that queries Tiktok."""

    name = "tiktok_search"
    description = (
        "search for tiktok videos associated with a query string."
    )
    args_schema: Type[BaseModel] = TiktokSearchInput

    credentials: CredentialsSchemaBase

    async def _search(self, query: str, max_count: int):
        response = await CredentialsHelper.request(
            "POST",
            SEARCH_URL,
            credentials=self.credentials,
            json={
                "max_count": max_count,
            }
        )
        print("response: ", response)

        return response

    def _run(self, query: str, max_count: int):
        return runnify(self._search)(query, max_count)

    # 这里不能用 position arg, 和 langchain 的实现有关
    async def _arun(self, query: str, max_count: int):        
        return await self._search(query, max_count)
