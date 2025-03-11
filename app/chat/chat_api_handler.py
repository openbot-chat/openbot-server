from typing import Dict, Any

from channels.connection import Connection
from channels.api.api_handler import APIHandler
from channels.manager.hub_manager import HubManager
from models.chat import ChatMessage
from uuid import uuid4
from .handler import AsyncChatResponseCallbackHandler
from db.session import async_session
from repositories.sqlalchemy.agent_repository import AgentRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from repositories.sqlalchemy.conversation_repository import ConversationRepository
from repositories.sqlalchemy.message_repository import MessageRepository
from repositories.sqlalchemy.prompt_repository import PromptRepository
from services import (
    CredentialsService,
    ConversationService,
    PromptService,
)
from core.agent import AgentBuilder
from core.llm import LLMManager
from core.memory import MemoryManager
import traceback
from uuid import UUID
from redis.asyncio import Redis



class ChatAPIHandler(APIHandler):
  def __init__(
      self, 
      hub_manager: HubManager,
      llm_manager: LLMManager,
      memory_manager: MemoryManager,
      redis: Redis,
  ):
      super().__init__(hub_manager)
      self.llm_manager = llm_manager
      self.memory_manager = memory_manager
      self.redis = redis

  async def on_message(self, msg: Dict[str, Any], connection: Connection):
    print("新消息", msg)
    message = ChatMessage.parse_obj(msg)

    # 在这里使用会话对象
    # 例如：执行数据库操作
    async with async_session() as db_session:
        agent_repository = AgentRepository(db_session)
        agent = await agent_repository.get_by_id(UUID(message.to.id))
        credentials_repository = CredentialsRepository(db_session)
        credentials_service = CredentialsService(credentials_repository)
        prompt_repository = PromptRepository(db_session)
        prompt_service = PromptService(prompt_repository)
        message_repository = MessageRepository(db_session)
        conversation_repository = ConversationRepository(db_session)
        conversation_service = ConversationService(
            repository=conversation_repository, 
            message_repository=message_repository,
            agent_repository=agent_repository,
        )

        memory_type: str = "conversation_buffer_window" # from agent config
        memory_options = None
        if agent.options is not None:
            memory_options = agent.options.get('memory')
            if memory_options is not None:
                memory_options = memory_options.copy()
                memory_type = memory_options.pop('type', memory_type)

        print("memory_type: ", memory_type)
        memory = await self.memory_manager.build(memory_type, message.conversation_id, memory_options or {})

        if message.metadata is not None:
            agent_type = message.metadata.get("type")

        if agent_type is None:
            if agent is not None and agent.options is not None:
                agent_type = agent.options.get("type")

        agent_type = agent_type or "chat"

        agent_runner = await AgentBuilder.build_agent(
            agent_type=agent_type,
            agent=agent,
            conversation=conversation,
            llm_manager=self.llm_manager,
            memory=memory,
            credentials_service=credentials_service,
            conversation_service=conversation_service,
            prompt_service=prompt_service,
            redis=redis,
        )

        try:
            stream_handler = AsyncChatResponseCallbackHandler(connection=connection, agent=agent, message=message)
            response = await agent_runner.run(message, stream_handler=stream_handler)
        except Exception as e:
            print(traceback.format_exc())
            response = ChatMessage(
              id=str(uuid4()),
              conversation_id=message.conversation_id,
              text=str(e),
            )

        print('answer: ', response)
        await connection.send(response.dict())
        

  def on_error(self, err: Exception, connection: Connection):
    print('on_error: ', err)
