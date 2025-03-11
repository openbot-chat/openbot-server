import os
import traceback
import logging
from typing import List, Any, Dict, Optional

from core.tools.baidu_search import get_baidu_search_api
from models.chat import ChatMessage, ChatUser
from models.conversation import ConversationSchema

from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.base_language import BaseLanguageModel
from langchain.agents.tools import BaseTool, Tool
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory, RedisChatMessageHistory
from langchain.experimental.autonomous_agents.autogpt.agent import AutoGPT
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore

from vectorstore.datastore_manager import DatastoreManager

from uuid import uuid4
from models.agent import AgentSchema
from models.credentials import CredentialsSchemaBase
from services import CredentialsService
from datetime import datetime, date
from .agent import Agent
from core.llm import LLMManager
from core.agent_tool.agent_tool_retriever import AgentToolRetriever
from core.agent_tool.agent_tool_loader_manager import AgentToolLoaderManager



class AutoGPTAgent(Agent):
    agent: AgentSchema
    llm_manager: LLMManager
    credentials_service: CredentialsService
    agent_tool_retriever: AgentToolRetriever
    agent_tool_loader_manager: AgentToolLoaderManager



    async def load_tools(self, llm: BaseLanguageModel, query: str) -> List[BaseTool]:
        agent_tools = await self.agent_tool_retriever.retrieve(self.agent.id, query)
        logging.info(f'找到可以使用的 agent_tools: {len(agent_tools)}')

        tools: List[BaseTool] = []
        for agent_tool in agent_tools:
            credentials: Optional[CredentialsSchemaBase] = None
            credentials_id = agent_tool.options.get("credentials_id")
            if credentials_id is not None:
                credentials = await self.credentials_service.get_by_id(credentials_id)


            agent_tool_instances = await self.agent_tool_loader_manager.load(agent_tool, credentials)
            tools += agent_tool_instances
        logging.info(f'加载 agent tools => tools: {len(tools)}')

        # 默认tools
        default_tools = [
            web_search,
            # S3 WriteFileTool(root_dir="./data"),
            # S3 ReadFileTool(root_dir="./data"),
            # process_csv,
            # query_website_tool,
        ]

        tools.extend(default_tools)

        return tools
        


    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any)-> ChatMessage:
        TODAY = date.today().strftime("%Y-%m-%d")

        url = os.getenv("REDIS_URL")
        # 先将就用
        chat_history = RedisChatMessageHistory(url=url, ttl=600, session_id=message.conversation_id)

        memory = ConversationBufferWindowMemory(
            chat_memory=chat_history,
            memory_key="chat_history",
            output_key="output",
            return_messages=True,
        )


        stream_handler = kwargs.get('stream_handler')
        llm_config = None
        if 'llm' in self.agent.options:
            llm_config = self.agent.options['llm']


        llm_streaming = await self.llm_manager.load(llm_config, stream_handler=stream_handler)
        llm = await self.llm_manager.load(llm_config)
        
        openai_api_key = None
        if llm_config is not None:
            openai_api_key = llm_config.get('openai_api_key')

        embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)
        vectorstore = FAISS(embedding.embed_query, index, InMemoryDocstore({}), {})

        tools: List[BaseTool] = []
        tools += await self.load_tools(llm_streaming, message.text)


    
        agent = AutoGPT.from_llm_and_tools(
            ai_name="Tom",
            ai_role="Assistant",
            tools=tools,
            llm=llm_streaming,
            memory=vectorstore.as_retriever(search_kwargs={"k": 8}),
            # human_in_the_loop=True, # Set to True if you want to add feedback at each step.
        )
  
        try:
            answer = await agent.run([message.text])
        except Exception:
            chat_history.clear()
            answer = await agent.arun([message.text])

        print('answer: ', answer)

        sent_at = int(datetime.now().timestamp() * 1000)

        return ChatMessage(
            id=str(uuid4()),
            conversation_id=message.conversation_id,
            sent_at=sent_at,
            # text=answer['output'].replace("Answer: ", ''),
            from_user=ChatUser(
                id=str(self.agent.id),
                name=self.agent.name,
            ),
            to=ChatUser(
                id=message.from_user.id,
                name=message.from_user.name,
            ),
            metadata={
                # "thoughts": answer['intermediate_steps'], 
            }
        )