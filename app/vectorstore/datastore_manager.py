from typing import Dict, Any
from models.credentials import *
from .vectorstore import VectorStore
from .pinecone import PineconeVectorStore
from .qdrant import QdrantVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from config import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
)

import pinecone

pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENVIRONMENT,
)

class DatastoreManager():
    def __init__(self):
        ...

    @classmethod
    def get(cls, provider: str, options: Dict[str, Any]) -> VectorStore:
        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY
        )
  
        if provider == 'qdrant':
            return QdrantVectorStore(embeddings, options)
        elif provider == 'pinecone':
            return PineconeVectorStore(embeddings, options)
        else:
            raise NotImplementedError('datastore provider not found')