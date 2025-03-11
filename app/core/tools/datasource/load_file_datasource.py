from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import json
from asyncer import runnify
from services.datasource_service import DatasourceService
from models.datasource import CreateDatasourceSchema, DatasourceSchema
from uuid import UUID



class LoadFileDatasourceInput(BaseModel):
    url: str = Field(description="url")



class LoadFileDatasourceTool(BaseTool):
    """Tool that load file datasource."""

    name = "youtube_search"
    description = (
        "load file datasource with a given url."
    )
    datastore_id: UUID

    datasource_service: DatasourceService


    args_schema: Type[BaseModel] = LoadFileDatasourceInput

    async def _load(self, url: str) -> DatasourceSchema:
        return await self.datasource_service.create(CreateDatasourceSchema(
            name = "",
            type = "file",
            options = {
                "url": url,  
            },
            datastore_id = self.datastore_id,
        ))

        data = json.loads(results)
        # url_suffix_list = [video["url_suffix"] for video in data["videos"]]
        return data["videos"]

    def _run(self, url: str):
        return runnify(self._arun)(url)

    async def _arun(self, url: str):        
        return await self._load(url)
