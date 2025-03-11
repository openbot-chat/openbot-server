"""Class for a VectorStore-backed memory object."""

from typing import Any, Dict, List, Optional, Sequence, Union, Coroutine

from langchain.memory.chat_memory import BaseMemory
from langchain.memory.utils import get_prompt_input_key
from langchain.pydantic_v1 import Field
from langchain.schema import Document
from vectorstore.vectorstore import VectorStore
from vectorstore.models import DocumentQuery, DocumentMetadataFilter, Document as VDocument
from asyncer import syncify, runnify
import asyncio



class VectorStoreMemory(BaseMemory):
    """VectorStore-backed memory."""

    vectorstore: VectorStore = Field(exclude=True)
    """VectorStore object to connect to."""

    collection_name: str

    session_id: str

    memory_key: str = "history"  #: :meta private:
    """Key name to locate the memories in the result of load_memory_variables."""

    input_key: Optional[str] = None
    """Key name to index the inputs to load_memory_variables."""

    return_messages: bool = False
    """Whether or not to return the result of querying the database directly."""

    exclude_input_keys: Sequence[str] = Field(default_factory=tuple)
    """Input keys to exclude in addition to memory key when constructing the document"""

    @property
    def memory_variables(self) -> List[str]:
        """The list of keys emitted from the load_memory_variables method."""
        return [self.memory_key]

    def _get_prompt_input_key(self, inputs: Dict[str, Any]) -> str:
        """Get the input key for the prompt."""
        if self.input_key is None:
            return get_prompt_input_key(inputs, self.memory_variables)
        return self.input_key

    def load_memory_variables(
        self, inputs: Dict[str, Any]
    ) -> Dict[str, Union[List[Document], str]]:
        """Return history buffer."""
        input_key = self._get_prompt_input_key(inputs)
        query = inputs[input_key]

        async def do_single_query():
            return await self.vectorstore.single_query(self.collection_name, DocumentQuery(
                query=query,
                top_k=4,
                filter=DocumentMetadataFilter(
                    source_id=self.session_id,
                ),
            ))

        # r = runnify(do_single_query)()
        r = asyncio.run(do_single_query())

        docs = [Document(page_content=doc.text, metadata=doc.metadata) for doc in r.results]

        result: Union[List[Document], str]
        if not self.return_messages:
            result = "\n".join([doc.page_content for doc in docs])
        else:
            result = docs
        return {self.memory_key: result}

    def _form_documents(
        self, inputs: Dict[str, Any], outputs: Dict[str, str]
    ) -> List[Document]:
        """Format context from this conversation to buffer."""
        # Each document should only include the current turn, not the chat history
        exclude = set(self.exclude_input_keys)
        exclude.add(self.memory_key)
        filtered_inputs = {k: v for k, v in inputs.items() if k not in exclude}
        texts = [
            f"{k}: {v}"
            for k, v in list(filtered_inputs.items()) + list(outputs.items())
        ]
        page_content = "\n".join(texts)
        return [Document(page_content=page_content)]

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        documents = self._form_documents(inputs, outputs)

        vdocs = [VDocument(
            text=document.page_content, 
            metadata={
                "source_id": self.session_id,
            }
        ) for document in documents]
        
        asyncio.run(self.vectorstore.upsert(self.collection_name, vdocs))

    def clear(self) -> None:
        """Nothing to clear."""
