from typing import Any
from abc import abstractmethod
from models.chat import ChatMessage
from models.conversation import ConversationSchema
from models.message import *
from pydantic import BaseModel
from services.conversation_service import ConversationService
from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory import ChatMessageHistory
from schemas.pagination import CursorParams
from core.apm.telemetry import tracer
from uuid import uuid4


MAX_WINDOW_SIZE = 10


class Agent(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    conversation_service: ConversationService
    memory: BaseChatMemory

    @abstractmethod
    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any) -> ChatMessage:
        ...

    # @tracer.start_as_current_span('agent-run0')
    async def run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any) -> ChatMessage:
        with tracer.start_as_current_span("agent-run") as span:
            run_id = str(uuid4())

            span.set_attributes({
                "run_id": run_id
            })

            span.add_event(
                "pre-run",
                {
                    "conversation": str(conversation.id),
                },
            )

            await self._pre_run(conversation)
            output = await self._run(conversation, message, **kwargs)
            await self._post_run(conversation, message, output)
            return output

    async def _pre_run(self, conversation: ConversationSchema):
        # 如果是纯内存型 memory, 则要从 持久化中获取消息并填充 history
        if isinstance(self.memory.chat_memory, ChatMessageHistory):
            message_page = await self.conversation_service.list_messages(str(conversation.id), CursorParams(
                size=MAX_WINDOW_SIZE,
            ))

            messages = message_page.items[::-1]
            [
                self.memory.chat_memory.add_ai_message(message.text)
                if message.type == "ai"
                else self.memory.chat_memory.add_user_message(message.text)
                for message in messages
            ]


    async def _post_run(self, conversation: ConversationSchema, message: ChatMessage, output: ChatMessage):
        with tracer.start_as_current_span("agent-post-run"):
            await self.conversation_service.add_message(CreateMessageSchema(
                agent_id=str(conversation.agent_id),
                conversation_id=str(conversation.id),
                type="human",
                text=message.text or "",
            ))
            await self.conversation_service.add_message(CreateMessageSchema(
                agent_id=str(conversation.agent_id),
                conversation_id=str(conversation.id),
                type="ai",
                text=output.text or "",
            ))