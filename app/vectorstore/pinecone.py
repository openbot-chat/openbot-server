import uuid
from typing import Any, List, Optional, Dict

from .vectorstore import VectorStore, DocumentChunk
from tenacity import retry, wait_random_exponential, stop_after_attempt
import asyncio

import pinecone

from langchain.vectorstores import Pinecone
from langchain.vectorstores.base import VectorStore as LangchainVectorStore
from langchain.embeddings.base import Embeddings
from .models import *
from .date import to_unix_timestamp


UPSERT_BATCH_SIZE = 100


class PineconeVectorStore(VectorStore):
    def __init__(self, embeddings: Embeddings, options: Dict[str, Any]):
        super().__init__(embeddings)
        index_name = str(options.get("index_name"))
        self.index = pinecone.Index(index_name)

    async def create_collection(self, collection_name: str, **kwargs) -> bool:
        distance_func = kwargs.get("distance_func", "Cosine")
        distance_func = distance_func.upper()
        # TODO 暂时忽略, pinecone 创建 index 代价昂贵

    def delete_collection(self, namespace: str) -> bool:
        r = self.index.delete(delete_all=True, namespace=namespace)
        print('delete_collection r: ', r)
        return True

    async def _upsert(self, collection_name: str, chunks: Dict[str, List[DocumentChunk]]) -> Dict[str, List[DocumentChunk]]:
        """
        Takes in a dict from document id to list of document chunks and inserts them into the index.
        Return a list of document ids.
        """

        # Initialize a list of ids to return
        doc_ids: List[str] = []
        # Initialize a list of vectors to upsert
        vectors = []
        # Loop through the dict items
        for doc_id, chunk_list in chunks.items():
            # Append the id to the ids list
            doc_ids.append(doc_id)
            print(f"Upserting document_id: {doc_id}")
            for chunk in chunk_list:
                # Create a vector tuple of (id, embedding, metadata)
                # Convert the metadata object to a dict with unix timestamps for dates
                pinecone_metadata = self._get_pinecone_metadata(chunk.metadata)
                # Add the text and document id to the metadata dict
                pinecone_metadata["text"] = chunk.text
                pinecone_metadata["document_id"] = doc_id
                vector = (chunk.id, chunk.embedding, pinecone_metadata)
                vectors.append(vector)

        # Split the vectors list into batches of the specified size
        batches = [
            vectors[i : i + UPSERT_BATCH_SIZE]
            for i in range(0, len(vectors), UPSERT_BATCH_SIZE)
        ]
        # Upsert each batch to Pinecone
        for batch in batches:
            try:
                print(f"Upserting batch of size {len(batch)}")
                self.index.upsert(vectors=batch, namespace=collection_name)
                print(f"Upserted batch successfully")
            except Exception as e:
                print(f"Error upserting batch: {e}")
                raise e

        return chunks


    def _get_pinecone_filter(
        self, filter: Optional[DocumentMetadataFilter] = None
    ) -> Dict[str, Any]:
        if filter is None:
            return {}

        pinecone_filter = {}

        # For each field in the MetadataFilter, check if it has a value and add the corresponding pinecone filter expression
        # For start_date and end_date, uses the $gte and $lte operators respectively
        # For other fields, uses the $eq operator
        for field, value in filter.dict().items():
            if value is not None:
                if field == "start_date":
                    pinecone_filter["date"] = pinecone_filter.get("date", {})
                    pinecone_filter["date"]["$gte"] = to_unix_timestamp(value)
                elif field == "end_date":
                    pinecone_filter["date"] = pinecone_filter.get("date", {})
                    pinecone_filter["date"]["$lte"] = to_unix_timestamp(value)
                else:
                    pinecone_filter[field] = value

        return pinecone_filter


    def _get_pinecone_metadata(
        self, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if metadata is None:
            return {}

        pinecone_metadata = {}

        # For each field in the Metadata, check if it has a value and add it to the pinecone metadata dict
        # For fields that are dates, convert them to unix timestamps
        for field, value in metadata.items():
            if value is not None:
                if field in ["created_at"]:
                    pinecone_metadata[field] = to_unix_timestamp(value)
                else:
                    pinecone_metadata[field] = value

        return pinecone_metadata



    async def _single_query(
        self,
        collection_name: str,
        query: QueryWithEmbedding,
    ) -> DocumentQueryResult:
        raise NotImplementedError

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    async def _query(
        self,
        collection_name: str,
        queries: List[QueryWithEmbedding],
    ) -> List[DocumentQueryResult]:
        """
        Takes in a list of queries with embeddings and filters and returns a list of query results with matching document chunks and scores.
        """

        # Define a helper coroutine that performs a single query and returns a QueryResult
        async def _single_query(query: QueryWithEmbedding) -> DocumentQueryResult:
            print(f"Query: {query.query}")

            # Convert the metadata filter object to a dict with pinecone filter expressions
            pinecone_filter = self._get_pinecone_filter(query.filter)

            try:
                # Query the index with the query embedding, filter, and top_k
                query_response = self.index.query(
                    namespace=collection_name,
                    top_k=query.top_k,
                    vector=query.embedding,
                    filter=pinecone_filter,
                    include_metadata=True,
                )
            except Exception as e:
                print(f"Error querying index: {e}")
                raise e

            query_results: List[DocumentChunkWithScore] = []
            for result in query_response.matches:
                score = result.score
                metadata = result.metadata
                # Remove document id and text from metadata and store it in a new variable
                metadata_without_text = (
                    {key: value for key, value in metadata.items() if key != "text"}
                    if metadata
                    else None
                )

                # Create a document chunk with score object with the result data
                result = DocumentChunkWithScore(
                    id=result.id,
                    score=score,
                    text=metadata["text"] if metadata and "text" in metadata else None,
                    metadata=metadata_without_text,
                )
                query_results.append(result)
            return DocumentQueryResult(query=query.query, results=query_results)

        # Use asyncio.gather to run multiple _single_query coroutines concurrently and collect their results
        results: List[DocumentQueryResult] = await asyncio.gather(
            *[_single_query(query) for query in queries]
        )

        return results



    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    async def delete(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        """
        Removes vectors by ids, filter, or everything from the index.
        """
        # Delete all vectors from the index if delete_all is True
        if delete_all == True:
            try:
                print(f"Deleting all vectors from index")
                self.index.delete(delete_all=True, namespace=collection_name)
                print(f"Deleted all vectors successfully")
                return True
            except Exception as e:
                print(f"Error deleting all vectors: {e}")
                raise e

        # Convert the metadata filter object to a dict with pinecone filter expressions
        pinecone_filter = self._get_pinecone_filter(filter)
        # Delete vectors that match the filter from the index if the filter is not empty
        if pinecone_filter != {}:
            try:
                print(f"Deleting vectors with filter {pinecone_filter}")
                self.index.delete(filter=pinecone_filter, namespace=namespace)
                print(f"Deleted vectors with filter successfully")
            except Exception as e:
                print(f"Error deleting vectors with filter: {e}")
                raise e

        # Delete vectors that match the document ids from the index if the ids list is not empty
        if ids != None and len(ids) > 0:
            try:
                print(f"Deleting vectors with ids {ids}")
                pinecone_filter = {"document_id": {"$in": ids}}
                self.index.delete(filter=pinecone_filter, namespace=namespace)  # type: ignore
                print(f"Deleted vectors with ids successfully")
            except Exception as e:
                print(f"Error deleting vectors with ids: {e}")
                raise e

        return True        



    def as_langchain(self, collection_name: str, embeddings: Embeddings, content_payload_key: str = 'text', **kwargs: Any) -> LangchainVectorStore:
        return Pinecone(
            index=self.index,
            embedding=embeddings,
            namespace=collection_name,
            text_key=content_payload_key,
            **kwargs,
        )
