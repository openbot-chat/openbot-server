from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import json
from asyncer import asyncify



class YoutubeSearchInput(BaseModel):
    query: str = Field(description="Query string", default="hot video")
    num_results: int = Field(description="maximum number of video results", default=4, max=10)



class YouTubeSearchTool(BaseTool):
    """Tool that queries YouTube."""

    name = "youtube_search"
    description = (
        "search for youtube videos associated with a query string."
        "You should enter query as search string."
        "You should enter num_results as the maximum number of video results."
    )

    args_schema: Type[BaseModel] = YoutubeSearchInput

    def _search(self, query: str, num_results: int) -> str:
        from youtube_search import YoutubeSearch
        
        results = YoutubeSearch(query, num_results).to_json()
        data = json.loads(results)
        # url_suffix_list = [video["url_suffix"] for video in data["videos"]]
        return data["videos"]

    def _run(self, query: str, num_results: int = 4):
        return self._search(query, num_results)

    # 这里不能用 position arg, 和 langchain 的实现有关
    async def _arun(self, query: str, num_results: int = 4):        
        return await asyncify(self._run)(query, num_results=num_results)
