import os
import traceback
import logging
from typing import Any, Dict
from models.chat import ChatMessage, ChatUser
from models.agent import AgentSchema
from models.conversation import ConversationSchema

from langchain.embeddings import OpenAIEmbeddings
from langchain_experimental.generative_agents import (
    GenerativeAgent as LGenerativeAgent,
    GenerativeAgentMemory,
)
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from chat.handler import SSEChatResponseCallbackHandler, AsyncSSEChatResponseCallbackHandler

from datetime import datetime

from .agent import Agent
from uuid import uuid4
from core.llm import LLMManager
from vectorstore.datastore_manager import DatastoreManager
from services import CredentialsService
from asyncer import asyncify
from config import (
    DEFAULT_QDRANT_OPTIONS
)



class GenerativeAgent(Agent):
    agent: AgentSchema
    llm_manager: LLMManager
    credentials_service: CredentialsService



    async def create_new_memory_retriever(self):
        """Create a new vector store retriever unique to the agent."""

        embeddings = self.get_embeddings()

        collection_name = f'{self.agent.id}.memory'

        #_vectorstore = DatastoreManager.get('pinecone', {
        #    "index_name": os.getenv("PINECONE_MEMORY_INDEX"),
        #})
        _vectorstore = DatastoreManager.get('qdrant', DEFAULT_QDRANT_OPTIONS)

        await _vectorstore.create_collection(collection_name)
        vectorstore = _vectorstore.as_langchain(collection_name, embeddings, content_payload_key="text")

        return TimeWeightedVectorStoreRetriever(
            vectorstore=vectorstore, other_score_keys=["importance"], k=15
        )

    def get_embeddings(self):
        llm_config = None
        if 'llm' in self.agent.options:
            llm_config = self.agent.options['llm']

        openai_api_key = None
        if llm_config is not None:
            openai_api_key = llm_config.get('openai_api_key')
        return OpenAIEmbeddings(openai_api_key=openai_api_key)

    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any)-> ChatMessage:
        options = self.agent.options or {}
        llm = await self.llm_manager.load(options.get('llm'), **kwargs)

        if "stream_handler" in kwargs:
            stream_handler = kwargs.get('stream_handler')

            if isinstance(stream_handler, AsyncSSEChatResponseCallbackHandler):
                llm.callbacks = [SSEChatResponseCallbackHandler(send=stream_handler.send)]

        memory_retriever = await self.create_new_memory_retriever()

        memory = GenerativeAgentMemory(
            llm=llm,
            memory_retriever=memory_retriever,
            verbose=True,
            reflection_threshold=8,  # we will give this a relatively low number to show how reflection works
        )

        chain: Dict[str, Any] = {}
        if self.agent.options is not None:
            chain = self.agent.options.get("chain", {})

        agent = LGenerativeAgent(
            name=self.agent.name,
            age=chain.get('age', 25),
            traits=chain.get("traits", "talkative"),  # You can add more persistent traits here
            status=chain.get("status", "N/A"),  # When connected to a virtual world, we can have the characters update their status
            llm=llm,
            memory=memory,
        )

        try:
            text = f"{message.from_user.name} says {message.text}"
            response = await asyncify(agent.generate_dialogue_response)(text)
        except Exception:
            print(traceback.format_exc())
            response = "LLM output error"
        
        sent_at = int(datetime.now().timestamp() * 1000)

        return ChatMessage(
            id=str(uuid4()),
            conversation_id=message.conversation_id,
            from_user=ChatUser(
                id=str(self.agent.id),
                name=self.agent.name,
            ),
            to=ChatUser(
                id=message.from_user.id,
                name=message.from_user.name,
            ),
            text=response[1],
            sent_at=sent_at,
            metadata={
            },
        )