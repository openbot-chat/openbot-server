import uuid
from typing import Any, List, Optional, Dict

from .vectorstore import VectorStore, DocumentChunk

from qdrant_client import QdrantClient
from qdrant_client.http.api_client import AsyncApis, AsyncApiClient
from qdrant_client.http import models as rest
from qdrant_client import grpc
from qdrant_client.conversions.conversion import RestToGrpc, GrpcToRest
from qdrant_client.conversions.conversion import grpc_to_payload

from langchain.vectorstores import Qdrant
from langchain.vectorstores.base import VectorStore as LangchainVectorStore
from langchain.embeddings.base import Embeddings
from .models import *
from .date import to_unix_timestamp
from asyncer import asyncify



class QdrantVectorStore(VectorStore):
    UUID_NAMESPACE = uuid.UUID("3896d314-1e95-4a3a-b45a-945f9f0b541d")

    def __init__(self, embeddings: Embeddings, options: Dict[str, Any]):
        self.async_client = AsyncApis[AsyncApiClient](
            host=options.get("url"),
            headers={
                "api-key": options.get("api_key"),
            }
        )
        self.client = QdrantClient(
            url=options.get("url"),
            prefer_grpc=options.get("prefer_grpc", True),
            api_key=options.get("api_key"),
        )
        super().__init__(embeddings)

    # TODO 要改成异步
    async def create_collection(self, collection_name: str, **kwargs: Any) -> bool:
        """
        self.client.async_grpc_collections.Get(
            grpc.GetCollectionInfoRequest(
                collection_name=collection_name,
            )
        )
        """

        def create() -> bool:
            try:
                self.client.get_collection(collection_name)
                return True
            except Exception:
                distance_func = kwargs.get("distance_func", "Cosine")
                distance_func = distance_func.upper()
                return self.client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=rest.VectorParams(
                        size=1536,
                        distance=rest.Distance[distance_func],
                    )
                )
        return await asyncify(create)()


    def delete_collection(self, collection_name: str) -> bool:
        return self.client.delete_collection(collection_name=collection_name)

    async def _upsert(self, collection_name: str, chunks: Dict[str, List[DocumentChunk]]) -> Dict[str, List[DocumentChunk]]:
        points = [
            self._convert_document_chunk_to_point(chunk)
            for _, chunks in chunks.items()
            for chunk in chunks
        ]

        """self.client.upsert(
            collection_name=collection_name,
            points=points,  # type: ignore
            wait=True,
        )
        """

        await self.client.async_grpc_points.Upsert(
            grpc.UpsertPoints(
                collection_name=collection_name,
                points=[RestToGrpc.convert_point_struct(point) for point in points],
            )
        )

        return chunks

    def _convert_document_chunk_to_point(
        self, document_chunk: DocumentChunk
    ) -> rest.PointStruct:
        created_at = (
            to_unix_timestamp(document_chunk.metadata.get('created_at'))
            if document_chunk.metadata.get('created_at') is not None
            else None
        )
        return rest.PointStruct(
            id=self._create_document_chunk_id(document_chunk.id),
            vector=document_chunk.embedding,  # type: ignore
            payload={
                "id": document_chunk.id,
                "text": document_chunk.text,
                "metadata": document_chunk.metadata,
                "created_at": created_at,
            },
        )

    def _create_document_chunk_id(self, external_id: Optional[str]) -> str:
        if external_id is None:
            return uuid.uuid4().hex
        return uuid.uuid5(self.UUID_NAMESPACE, external_id).hex
    
    def _convert_scored_point_to_document_chunk_with_score(
        self, scored_point: rest.ScoredPoint
    ) -> DocumentChunkWithScore:
        payload = scored_point.payload or {}
        return DocumentChunkWithScore(
            id=payload.get("id"),
            text=scored_point.payload.get("text"),  # type: ignore
            metadata=scored_point.payload.get("metadata"),  # type: ignore
            embedding=scored_point.vector,  # type: ignore
            score=scored_point.score,
        )

    def _convert_grpc_scored_point_to_document_chunk_with_score(
        self, scored_point: Any
    ) -> DocumentChunkWithScore:
        payload = grpc_to_payload(scored_point.payload) or {}

        return DocumentChunkWithScore(
            id=payload.get("id"),
            text=payload.get("text"),  # type: ignore
            metadata=payload.get('metadata'), # type: ignore
            # embedding=scored_point.vector,  # type: ignore
            score=scored_point.score,
        )



    async def _single_query(
        self,
        collection_name: str,
        query: QueryWithEmbedding,
    ) -> DocumentQueryResult:
        """
        result = await asyncify(self.client.search)(
            collection_name=collection_name,
            query_filter=self._convert_metadata_filter_to_qdrant_filter(query.filter),
            query_vector=query.embedding,
            limit=query.top_k or 4,
            score_threshold=query.score_threshold,
            offset=query.offset,
            with_payload=True,
            with_vectors=False,
        )
        """

        qdrant_filter = self._convert_metadata_filter_to_qdrant_filter(query.filter)
        if qdrant_filter is not None and isinstance(qdrant_filter, rest.Filter):
            qdrant_filter = RestToGrpc.convert_filter(qdrant_filter)

        response = await self.client.async_grpc_points.Search(
            grpc.SearchPoints(
                collection_name=collection_name,
                # vector_name=self.vector_name,
                vector=query.embedding,
                filter=qdrant_filter,
                # params=search_params,
                limit=query.top_k or 4,
                offset=query.offset,
                with_payload=grpc.WithPayloadSelector(enable=True),
                with_vectors=grpc.WithVectorsSelector(enable=True),
                score_threshold=query.score_threshold,
                # read_consistency=consistency,
            )
        )

        return DocumentQueryResult(
            query=query.query,
            results=[
                self._convert_grpc_scored_point_to_document_chunk_with_score(point)
                for point in response.result
            ],
        )
  



    async def _query(
        self,
        collection_name: str,
        queries: List[QueryWithEmbedding],
    ) -> List[DocumentQueryResult]:
        """
        Takes in a list of queries with embeddings and filters and returns a list of query results with matching document chunks and scores.
        """
        search_requests = [
            self._convert_query_to_search_request(query) for query in queries
        ]

        """
        results = await asyncify(self.client.search_batch)(
            collection_name=collection_name,
            requests=search_requests,
        )
        """

        search_requests = [RestToGrpc.convert_search_request(search_request, collection_name) for search_request in search_requests]

        response = await self.client.async_grpc_points.SearchBatch(
            grpc.SearchBatchPoints(
                collection_name=collection_name,
                search_points=search_requests,
            )
        )

        return [
            DocumentQueryResult(
                query=query.query,
                results=[
                    self._convert_grpc_scored_point_to_document_chunk_with_score(point)
                    for point in result.result
                ],
            )
            for query, result in zip(queries, response.result)
        ]

    def _convert_query_to_search_request(
        self, query: QueryWithEmbedding
    ) -> rest.SearchRequest:
        return rest.SearchRequest(
            vector=query.embedding,
            filter=self._convert_metadata_filter_to_qdrant_filter(query.filter),
            limit=query.top_k,  # type: ignore
            with_payload=True,
            with_vector=False,
        )



    async def delete(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        """
        Removes vectors by ids, filter, or everything in the datastore.
        Returns whether the operation was successful.
        """
        if ids is None and filter is None and delete_all is None:
            raise ValueError(
                "Please provide one of the parameters: ids, filter or delete_all."
            )

        if delete_all:
            points_selector = rest.Filter()
        else:
            points_selector = self._convert_metadata_filter_to_qdrant_filter(
                filter, ids
            )

        if points_selector is not None and isinstance(points_selector, rest.Filter):
            points_selector = RestToGrpc.convert_points_selector(rest.FilterSelector(filter=points_selector))

        response = await self.client.async_grpc_points.Delete(
            grpc.DeletePoints(
                collection_name=collection_name,
                points=points_selector,
            )
        )
        
        """
        response = self.client.delete(
            collection_name=collection_name,
            points_selector=points_selector,  # type: ignore
        )
        """

        response = GrpcToRest.convert_update_result(response.result)
        return rest.UpdateStatus.ACKNOWLEDGED == response.status

    def _convert_metadata_filter_to_qdrant_filter(
        self,
        metadata_filter: Optional[DocumentMetadataFilter] = None,
        ids: Optional[List[str]] = None,
    ) -> Optional[rest.Filter]:
        if metadata_filter is None and ids is None:
            return None

        must_conditions, should_conditions = [], []

        # Filtering by document ids
        if ids and len(ids) > 0:
            for document_id in ids:
                should_conditions.append(
                    rest.FieldCondition(
                        key="metadata.document_id",
                        match=rest.MatchValue(value=document_id),
                    )
                )

        # Equality filters for the payload attributes
        if metadata_filter:
            meta_attributes_keys = {
                "document_id": "metadata.document_id",
                "source": "metadata.source",
                "source_id": "metadata.source_id",
                "author": "metadata.author",
            }

            for meta_attr_name, payload_key in meta_attributes_keys.items():
                attr_value = getattr(metadata_filter, meta_attr_name)
                if attr_value is None:
                    continue

                must_conditions.append(
                    rest.FieldCondition(
                        key=payload_key, match=rest.MatchValue(value=attr_value)
                    )
                )

            # Date filters use range filtering
            start_date = metadata_filter.start_date
            end_date = metadata_filter.end_date
            if start_date or end_date:
                gte_filter = (
                    to_unix_timestamp(start_date) if start_date is not None else None
                )
                lte_filter = (
                    to_unix_timestamp(end_date) if end_date is not None else None
                )
                must_conditions.append(
                    rest.FieldCondition(
                        key="created_at",
                        range=rest.Range(
                            gte=gte_filter,
                            lte=lte_filter,
                        ),
                    )
                )

        if 0 == len(must_conditions) and 0 == len(should_conditions):
            return None

        return rest.Filter(must=must_conditions, should=should_conditions)



    def as_langchain(self, collection_name: str, embeddings: Embeddings, content_payload_key: str = 'text', **kwargs: Any) -> LangchainVectorStore:
        return Qdrant(
            client=self.client,
            collection_name=collection_name,
            embeddings=embeddings,
            content_payload_key=content_payload_key,
            **kwargs,
        )
