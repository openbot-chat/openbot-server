import qdrant_client
from vectorstore.vectorstore import VectorStore
from vectorstore.qdrant import QdrantVectorStore

from langchain.embeddings.openai import OpenAIEmbeddings
from config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    OPENAI_API_KEY
)


### 暂时没用了，用 DatastoreManager 取代了

def create_vectorstore() -> VectorStore:
    options = {
      "url": QDRANT_URL,
      "api_key": QDRANT_API_KEY,
      "prefer_grpc": True,
    }
 
    openai_api_key = OPENAI_API_KEY

    embeddings = OpenAIEmbeddings(
        openai_api_key=openai_api_key
    )

    return QdrantVectorStore(
        embeddings=embeddings,
        options=options,
    )