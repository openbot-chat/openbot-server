from typing import Any, List, Dict, Tuple
from abc import ABC, abstractmethod
from .models import *
from tenacity import retry, wait_random_exponential, stop_after_attempt
import asyncio
import uuid
import tiktoken
from hashlib import md5

from langchain.vectorstores import VectorStore as LangchainVectorStore
from langchain.embeddings.base import Embeddings

MIN_CHUNK_SIZE_CHARS = 350  # The minimum size of each text chunk in characters
MIN_CHUNK_LENGTH_TO_EMBED = 5
EMBEDDINGS_BATCH_SIZE = 128
MAX_NUM_CHUNKS = 10000

# Global variables
tokenizer = tiktoken.get_encoding(
    "cl100k_base"
)


class VectorStore(ABC):
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings

    @abstractmethod
    async def _upsert(self, collection_name: str, chunks: Dict[str, List[DocumentChunk]]) -> Dict[str, List[DocumentChunk]]:
        """
        Takes in a list of list of document chunks and inserts them into the database.
        Return a list of document ids.
        """
        raise NotImplementedError

    @abstractmethod
    async def _query(
        self, 
        collection_name: str, 
        queries: List[QueryWithEmbedding],
    ) -> List[DocumentQueryResult]:
        raise NotImplementedError

    @abstractmethod
    async def _single_query(
        self,
        collection_name: str,
        query: QueryWithEmbedding,
    ) -> DocumentQueryResult:
        raise NotImplementedError


    @abstractmethod
    async def create_collection(self, collection_name: str) -> bool:
        raise NotImplemented

    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        raise NotImplemented

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
      return self.embeddings.embed_documents(texts)


    def create_document_chunks(
        self,
        doc: Document, chunk_token_size: Optional[int]
    ) -> Tuple[List[DocumentChunk], str]:
        """
        Create a list of document chunks from a document object and return the document id.

        Args:
            doc: The document object to create chunks from. It should have a text attribute and optionally an id and a metadata attribute.
            chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

        Returns:
            A tuple of (doc_chunks, doc_id), where doc_chunks is a list of document chunks, each of which is a DocumentChunk object with an id, a document_id, a text, and a metadata attribute,
            and doc_id is the id of the document object, generated if not provided. The id of each chunk is generated from the document id and a sequential number, and the metadata is copied from the document object.
        """
        # Check if the document text is empty or whitespace
        if not doc.text or doc.text.isspace():
            return [], doc.id or str(uuid.uuid4())

        # Generate a document id if not provided
        # doc_id = doc.id or str(uuid.uuid4())
        doc_id = doc.id or md5(doc.text.encode("utf-8")).hexdigest()

        # Split the document text into chunks
        text_chunks = self.get_text_chunks(doc.text, chunk_token_size)

        metadata = {**(doc.metadata or {})}

        metadata['document_id'] = doc_id

        # Initialize an empty list of chunks for this document
        doc_chunks = []

        # Assign each chunk a sequential number and create a DocumentChunk object
        for i, text_chunk in enumerate(text_chunks):
            chunk_id = f"{doc_id}_{i}"
            doc_chunk = DocumentChunk(
                id=chunk_id,
                text=text_chunk,
                metadata=metadata,
            )
            # Append the chunk object to the list of chunks for this document
            doc_chunks.append(doc_chunk)

        # Return the list of chunks and the document id
        return doc_chunks, doc_id

    def get_text_chunks(self, text: str, chunk_token_size: Optional[int], chunk_size: int = 200) -> List[str]:
        """
        Split a text into chunks of ~CHUNK_SIZE tokens, based on punctuation and newline boundaries.

        Args:
            text: The text to split into chunks.
            chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

        Returns:
            A list of text chunks, each of which is a string of ~CHUNK_SIZE tokens.
        """
        # Return an empty list if the text is empty or whitespace
        if not text or text.isspace():
            return []

        # Tokenize the text
        tokens = tokenizer.encode(text, disallowed_special=())

        # Initialize an empty list of chunks
        chunks = []

        # Use the provided chunk token size or the default one
        chunk_size = chunk_token_size or chunk_size

        # Initialize a counter for the number of chunks
        num_chunks = 0

        # Loop until all tokens are consumed
        while tokens and num_chunks < MAX_NUM_CHUNKS:
            # Take the first chunk_size tokens as a chunk
            chunk = tokens[:chunk_size]

            # Decode the chunk into text
            chunk_text = tokenizer.decode(chunk)

            # Skip the chunk if it is empty or whitespace
            if not chunk_text or chunk_text.isspace():
                # Remove the tokens corresponding to the chunk text from the remaining tokens
                tokens = tokens[len(chunk) :]
                # Continue to the next iteration of the loop
                continue

            # Find the last period or punctuation mark in the chunk
            last_punctuation = max(
                chunk_text.rfind("."),
                chunk_text.rfind("?"),
                chunk_text.rfind("!"),
                chunk_text.rfind("\n"),
            )

            # If there is a punctuation mark, and the last punctuation index is before MIN_CHUNK_SIZE_CHARS
            if last_punctuation != -1 and last_punctuation > MIN_CHUNK_SIZE_CHARS:
                # Truncate the chunk text at the punctuation mark
                chunk_text = chunk_text[: last_punctuation + 1]

            # Remove any newline characters and strip any leading or trailing whitespace
            chunk_text_to_append = chunk_text.replace("\n", " ").strip()

            if len(chunk_text_to_append) > MIN_CHUNK_LENGTH_TO_EMBED:
                # Append the chunk text to the list of chunks
                chunks.append(chunk_text_to_append)

            # Remove the tokens corresponding to the chunk text from the remaining tokens
            tokens = tokens[len(tokenizer.encode(chunk_text, disallowed_special=())) :]

            # Increment the number of chunks
            num_chunks += 1

        # Handle the remaining tokens
        if tokens:
            remaining_text = tokenizer.decode(tokens).replace("\n", " ").strip()
            if len(remaining_text) > MIN_CHUNK_LENGTH_TO_EMBED:
                chunks.append(remaining_text)

        return chunks

    def get_document_chunks(
        self,
        documents: List[Document], chunk_token_size: Optional[int]
    ) -> Dict[str, List[DocumentChunk]]:
        """
        Convert a list of documents into a dictionary from document id to list of document chunks.

        Args:
          documents: The list of documents to convert.
          chunk_token_size: The target size of each chunk in tokens, or None to use the default CHUNK_SIZE.

        Returns:
          A dictionary mapping each document id to a list of document chunks, each of which is a DocumentChunk object
          with text, metadata, and embedding attributes.
        """
        # Initialize an empty dictionary of lists of chunks
        chunks: Dict[str, List[DocumentChunk]] = {}

        # Initialize an empty list of all chunks
        all_chunks: List[DocumentChunk] = []
        # Loop over each document and create chunks
        for doc in documents:
            doc_chunks, doc_id = self.create_document_chunks(doc, chunk_token_size)
        
            # Append the chunks for this document to the list of all chunks
            all_chunks.extend(doc_chunks)

            # Add the list of chunks for this document to the dictionary with the document id as the key
            chunks[doc_id] = doc_chunks

        # Check if there are no chunks
        if not all_chunks:
            return {}

        # Get all the embeddings for the document chunks in batches, using get_embeddings
        embeddings: List[List[float]] = []
        for i in range(0, len(all_chunks), EMBEDDINGS_BATCH_SIZE):
            # Get the text of the chunks in the current batch
            batch_texts = [
                chunk.text for chunk in all_chunks[i : i + EMBEDDINGS_BATCH_SIZE]
            ]

            # Get the embeddings for the batch texts
            batch_embeddings = self.get_embeddings(batch_texts)

            # Append the batch embeddings to the embeddings list
            embeddings.extend(batch_embeddings)

        # Update the document chunk objects with the embeddings
        for i, chunk in enumerate(all_chunks):
            # Assign the embedding from the embeddings list to the chunk object
            chunk.embedding = embeddings[i]

        return chunks


    async def upsert(
        self, collection_name: str, documents: List[Document], chunk_token_size: Optional[int] = None
    ) -> Dict[str, List[DocumentChunk]]:
        """
        Takes in a list of documents and inserts them into the database.
        First deletes all the existing vectors with the document id (if necessary, depends on the vector db), then inserts the new ones.
        Return a list of document ids.
        """
        # Delete any existing vectors for documents with the input document ids
        await asyncio.gather(
            *[
                self.delete(
                    collection_name,
                    filter=DocumentMetadataFilter(
                        document_id=document.id,
                    ),
                    delete_all=False,
                )
                for document in documents
                if document.id
            ]
        )
        chunks = self.get_document_chunks(documents, chunk_token_size)
        return await self._upsert(collection_name, chunks)

    async def query(self, collection_name: str, queries: List[DocumentQuery]) -> List[DocumentQueryResult]:
        """
        Takes in a list of queries and filters and returns a list of query results with matching document chunks and scores.
        """
        # get a list of of just the queries from the Query list
        query_texts = [query.query for query in queries]
        query_embeddings = self.get_embeddings(query_texts)
        # hydrate the queries with embeddings
        queries_with_embeddings = [
            QueryWithEmbedding(**query.dict(), embedding=embedding)
            for query, embedding in zip(queries, query_embeddings)
        ]
        return await self._query(collection_name, queries_with_embeddings)

    async def single_query(
        self,
        collection_name: str,
        query: DocumentQuery,
    ) -> DocumentQueryResult:
        query_text = query.query
        query_embeddings = self.get_embeddings([query_text])

        # hydrate the queries with embeddings
        query_with_embeddings = QueryWithEmbedding(**query.dict(), embedding=query_embeddings[0])
        
        return await self._single_query(collection_name, query_with_embeddings)



    @abstractmethod
    async def delete(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        """
        Removes vectors by ids, filter, or everything in the datastore.
        Multiple parameters can be used at once.
        Returns whether the operation was successful.
        """
        raise NotImplementedError



    @abstractmethod
    def as_langchain(self, collection_name: str, embeddings: Embeddings, content_payload_key: str = 'text', **kwargs: Any) -> LangchainVectorStore:
        raise NotImplementedError