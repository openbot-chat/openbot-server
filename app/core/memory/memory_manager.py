from typing import Any, Optional, Dict
from langchain.schema import BaseMemory
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory, RedisChatMessageHistory, ChatMessageHistory
from core.memory.zep_memory import ZepMemory
from core.memory.vectorstore import VectorStoreMemory
from vectorstore.datastore_manager import DatastoreManager
from redis.asyncio import Redis

import os        
from config import (
    ZEP_API_URL,
    ZEP_API_KEY,
    DEFAULT_QDRANT_OPTIONS
)
from core.llm.manager import LLMManager


async def create_zep_memory(conversation_id: str, options: Dict[str, Any]):
    options = options or {}
    api_url = options.get("api_url", ZEP_API_URL)
    api_key = options.get("api_key", ZEP_API_KEY)

    return ZepMemory(
        session_id=conversation_id,
        url=api_url,
        api_key=api_key,
        memory_key="chat_history",
        return_messages=True,
    )

async def create_conversation_buffer_window_memory(conversation_id: str, options: Dict[str, Any]):
    chat_history = ChatMessageHistory()
    # chat_history = RedisChatMessageHistory(url=url, ttl=ttl, session_id=conversation_id)
    return ConversationBufferWindowMemory(
        chat_memory=chat_history,
        memory_key="chat_history",
        output_key="output",
        return_messages=True,
    )
    """
    memory = ConversationTokenBufferMemory(
        chat_memory=chat_history,
        memory_key="chat_history",
        output_key="output",
        return_messages=True,
    )
    """

async def create_conversation_summary_buffer_memory(conversation_id: str, options: Dict[str, Any]):
    chat_history = ChatMessageHistory()

    # ttl = options.get("ttl", 86400)

    llm_manager = LLMManager()
    llm = await llm_manager.load()

    # url = os.getenv("REDIS_URL")
    # chat_history = RedisChatMessageHistory(url=url, ttl=ttl, session_id=conversation_id)
    # chat_history = RedisChatMessageHistory(redis=self.redis, ttl=600, session_id=message.conversation_id)
    
    # XXX 如果每次 new 的话，summary 会被清掉
    return ConversationSummaryBufferMemory(
        llm=llm,
        chat_memory=chat_history,
        memory_key="chat_history",
        output_key="output",
        return_messages=True,
    )


async def create_vectorstore_memory(conversation_id: str, options: Dict[str, Any]):
    collection_name = options.get("collection_name", "memory")
    vectorstore = DatastoreManager.get('qdrant', DEFAULT_QDRANT_OPTIONS)

    return VectorStoreMemory(
        memory_key="chat_history",
        session_id=conversation_id,
        vectorstore=vectorstore,
        collection_name=collection_name,
        return_messages=True,
    )



memory_build_funcs = {
    "zep": create_zep_memory,
    "conversation_buffer_window": create_conversation_buffer_window_memory,
    "conversation_summary_buffer_memory": create_conversation_summary_buffer_memory,
    "vectorstore": create_vectorstore_memory,
}



class MemoryManager:
    async def build(self, type: str, conversation_id: str, options: Dict[str, Any] = {}) -> Optional[BaseMemory]:
        func = memory_build_funcs.get(type)
        if not func:
            return None

        return await func(conversation_id, options)