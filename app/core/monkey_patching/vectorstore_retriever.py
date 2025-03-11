from typing import List
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.docstore.document import Document
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForRetrieverRun,
)


async def _aget_relevant_documents(
    self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
) -> List[Document]:
    if self.search_type == "similarity":
        docs = await self.vectorstore.asimilarity_search(
            query, **self.search_kwargs
        )
    elif self.search_type == "similarity_score_threshold":
        docs_and_similarities = (
            await self.vectorstore.asimilarity_search_with_relevance_scores(
                query, **self.search_kwargs
            )
        )
        for doc, score in docs_and_similarities:
            doc.metadata["score"] = score

        docs = [doc for doc, _ in docs_and_similarities]
    elif self.search_type == "mmr":
        docs = await self.vectorstore.amax_marginal_relevance_search(
            query, **self.search_kwargs
        )
    else:
        raise ValueError(f"search_type of {self.search_type} not allowed.")
    return docs


VectorStoreRetriever._aget_relevant_documents = _aget_relevant_documents