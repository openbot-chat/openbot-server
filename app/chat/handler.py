
from pydantic import BaseModel
from typing import Any, Callable, Union, Awaitable, Dict, Optional, List

from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
from langchain.callbacks import AsyncIteratorCallbackHandler

from langchain.schema import LLMResult

from channels.connection import Connection
from models.chat import ChatMessage, ChatUser
from models.agent import AgentSchema
import asyncio
import json
from uuid import UUID 
from models.conversation import ConversationSchema
from models.run_step import RunStep, RunStepStatus, RunStepType
import datetime



class AsyncChatResponseCallbackHandler(AsyncCallbackHandler, BaseModel):
    connection: Connection
    message: ChatMessage
    agent: AgentSchema

    class Config:
        arbitrary_types_allowed = True

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        resp = ChatMessage(
           from_user=ChatUser(
              id=self.agent.id,
           ),
           to=ChatUser(
              id=self.message.from_user.id,
           ),
           text=token, 
           type="stream", 
           conversation_id=self.message.conversation_id
        )
        await self.connection.send(resp.dict())

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        resp = ChatMessage(
           from_user=ChatUser(
              id=self.agent.id,
              name=self.agent.name,
           ), 
           to=ChatUser(
              id=self.message.from_user.id,
              name=self.message.from_user.name,
           ),
           text="data: [DONE]",
           type="stream",
           conversation_id=self.message.conversation_id,
        )
        await self.connection.send(resp.dict())


class ChatResponseCallbackHandler(BaseCallbackHandler, BaseModel):
    connection: Connection
    message: ChatMessage
    agent: AgentSchema

    class Config:
        arbitrary_types_allowed = True

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # logging.info(f"on_llm_new_token: {token}")
        resp = ChatMessage(
           from_user=ChatUser(
              id=self.agent.id,
              name=self.agent.name,
           ), 
           to=ChatUser(
              id=self.message.id,
              name=self.message.name,
           ),
           text=token, 
           type="stream", 
           conversation_id=self.message.conversation_id,
        )
        
        async def do_async_work():
            await self.connection.send(resp.dict())
        asyncio.run(do_async_work())


    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # logging.info(f"on_llm_end: {response}")
        resp = ChatMessage(
           sender=ChatUser(
              id=self.agent.id,
              name=self.agent.name,
           ), 
           to=ChatUser(
              id=self.message.id,
              name=self.message.name,
           ),
           text="data: [DONE]", 
           type="stream", 
           conversation_id=self.message.conversation_id,
        )
        async def do_async_work():
            await self.connection.send(resp.dict())
        asyncio.run(do_async_work())




from starlette.types import Send


class SSEChatResponseCallbackHandler(BaseCallbackHandler, BaseModel):
    send: Send

    class Config:
        arbitrary_types_allowed = True

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # logging.debug(f'on_llm_new_token: {token}')
        json_data = {
            "delta": token,
        }
        async def do_async():
            await self.send(f"data: {json.dumps(json_data)}\n\n") 
        asyncio.run(do_async())

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        pass



class AsyncSSEChatResponseCallbackHandler(AsyncCallbackHandler, BaseModel):
    send: Send
    conversation: Optional[ConversationSchema] = None

    class Config:
        arbitrary_types_allowed = True

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # logging.debug(f'on_llm_new_token: {token}')
        json_data = {
            "delta": token,
        }
        await self.send(f"data: {json.dumps(json_data)}\n\n")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        pass

    async def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool starts running."""
        print('on_tool_start: ', input_str, run_id, kwargs)

    async def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        name: str,
        **kwargs: Any,
    ) -> None:
        """Run when tool ends running."""
        if not self.conversation:
            return

        print('on_tool_end: ', output, run_id, kwargs)
        tool_id = name

        json_data = {
            "event": "run_step.new",
            "data": {
                "id": str(run_id),
                "type": "tool_calls",
                "status": "completed",
                "completed_at": int(datetime.datetime.now().timestamp()*1000),
                "conversation_id": str(self.conversation.id),
                "step_details": {
                    "type": "function",
                    "function": {
                        "id": tool_id,
                        "arguments": {},
                        "output": output,
                    }
                },
            },
        }


        await self.send(f"data: {json.dumps(json_data)}\n\n")