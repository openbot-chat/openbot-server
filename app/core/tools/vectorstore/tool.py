from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from asyncer import runnify
from vectorstore.vectorstore import VectorStore
from vectorstore.models import DocumentQuery, Document
import json



class VectorstoreQueryInput(BaseModel):
    query: str = Field(description="The user query")
    top_k: int = Field(description="maximum number of results, must less than 5", default=4, max=5)

class VectorstoreQueryTool(BaseTool):
    """Tool that query from vectorstore."""

    name = "vectorstore_query"
    description = (
        "query documents from vectorstore associated with a query string."
        "You should enter query as query string."
        "You can enter top_k as the maximum number of results."
    )
    collection_name: str
    max_results: int = Field(default=5)
    score_threshold: float = Field(default=0.0)

    vectorstore: VectorStore

    args_schema: Type[BaseModel] = VectorstoreQueryInput

    async def _query(self, query: str, top_k: int):
        print('vectorstore query: ', query, top_k)
        result = await self.vectorstore.single_query(self.collection_name, DocumentQuery(
            query=query,
            top_k=top_k,
            score_threshold=self.score_threshold,
        ))

        # return json.dumps(result.results, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)
        return result.results

    def _run(self, query: str, top_k: int = 4):
        return runnify(self._query)(query, top_k or min(top_k, self.max_results))

    # 这里不能用 position arg, 和 langchain 的实现有关
    async def _arun(self, query: str, top_k: int = 4):
        return await self._query(query, min(top_k, self.max_results))





class VectorstoreUpsertInput(BaseModel):
    text: str = Field(description="text")

class VectorstoreUpsertTool(BaseTool):
    """Tool that upsert vectorstore."""

    name = "vectorstore_upsert"
    description = (
        "upsert data to vectorstore."
        "You should enter text to upsert"
    )
    collection_name: str

    vectorstore: VectorStore

    args_schema: Type[BaseModel] = VectorstoreUpsertInput

    async def _upsert(self, text: str):
        result = await self.vectorstore.upsert(self.collection_name, [
            Document(
                text=text,
                metadata={
                    "source_type": "vectorstore_tool",
                }
            )
        ])

        doc_id = None
        for k, v in result.items():
            doc_id = k
            break

        if not doc_id:
            return None
        else:
            return {
                "id": doc_id
            }

    def _run(self, text: str):
        return runnify(self._upsert)(text)

    # 这里不能用 position arg, 和 langchain 的实现有关
    async def _arun(self, text: str):        
        return await self._upsert(text)