
from typing import List, Union, Any

from fastapi import APIRouter, Depends, WebSocket, HTTPException, Request
from channels.websocket.connection import WebSocketConnection
from models.chat import ChatMessage, ChatUser
from models.api import MessageResponse

import traceback
from services import (
    AgentToolService, 
    AgentService, 
    CredentialsService, 
    ConversationService,
    PromptService,
    VoiceRecognizeService,
)
from datetime import datetime
from uuid import uuid4, UUID
from core.agent import AgentBuilder
import logging
import json
from starlette.types import Send
from chat.handler import AsyncSSEChatResponseCallbackHandler
from api.common.stream_response import StreamingResponse
from core.chat.message_routine import MessageRoutine 
from core.chat.voice_transcribe_processor import VoiceTranscribeProcessor 
from core.chat.image_transcribe_processor import ImageTranscribeProcessor
from core.image.image_cognitive_manager import ImageCognitiveManager
from api.dependencies.redis import get_redis
from redis.asyncio import Redis



router = APIRouter()

@router.websocket("/ws")
async def chat(
  websocket: WebSocket,
):
  api_handler = websocket.app.state.api_handler
  print('api_handler: ', api_handler)
  connection = WebSocketConnection(websocket, api_handler)
  await connection.serve()



def streaming_response(json_data, chat_generator):
  logging.info(f"Sending initial JSON: {json_data}")
  yield f"data: {json.dumps(json_data)}\n\n"  # NOTE: EventSource

  text = ""
  for chunk in chat_generator:
      text += chunk
      json_data['delta'] = chunk
      logging.info(f"Sending chunk: {json.dumps(json_data)}")
      yield f"data: {json.dumps(json_data)}\n\n"  # NOTE: EventSource

  json_data['text'] = text
  logging.info(f"reply: {text}")
  yield f"data: {json.dumps(json_data)}\n\n"  # NOTE: EventSource
  yield f"data: [DONE]\n\n"  # NOTE: EventSource


from langchain.docstore.document import Document
from core.agent.chat_agent import ChatAgent
from core.agent_tool.retrievers.database_retriever import DatabaseAgentToolRetriever



# 这个总结应该放到 documents 中去
@router.post('/summary', response_model=ChatMessage, response_model_exclude_none=True)
async def summary(
    message: ChatMessage,
    request: Request,
    credentials_service: CredentialsService = Depends(CredentialsService),
):
    docs = [
        Document(page_content=message.text),
    ]

    agent_runner = ChatAgent(None, request.app.state.llm_manager, credentials_service)
    summary = agent_runner.summary(docs)
    sent_at = int(datetime.now().timestamp() * 1000)

    return ChatMessage(
        id=str(uuid4()),
        text=summary,
        sent_at=sent_at,
        from_user=ChatUser(),
        conversation_id=message.conversation_id,
    )

@router.post('/send_message', response_model=MessageResponse, response_model_exclude_none=True)
async def send_message(
    message: ChatMessage, 
    request: Request,
    credentials_service: CredentialsService = Depends(CredentialsService),
    agent_service: AgentService = Depends(AgentService),
    agent_tool_service: AgentToolService = Depends(AgentToolService),
    conversation_service: ConversationService = Depends(ConversationService),
    voice_recognize_service: VoiceRecognizeService = Depends(VoiceRecognizeService),
    prompt_service: PromptService = Depends(PromptService),
    image_cognitive_manager: ImageCognitiveManager = Depends(ImageCognitiveManager),
    redis: Redis = Depends(get_redis),
):
    agent_tool_retriever = DatabaseAgentToolRetriever(agent_tool_service)
    

    message_routine = MessageRoutine()
    message_routine.add_processor(VoiceTranscribeProcessor(voice_recognize_service))
    message_routine.add_processor(ImageTranscribeProcessor(image_cognitive_manager))

    conversation = await conversation_service.get_by_id(UUID(hex=message.conversation_id))
    if not conversation:
        raise HTTPException(status_code=401, detail={
            "error": f"conversation {message.conversation_id} not found"
        })

    message.from_user = ChatUser(
        id=conversation.user_id or conversation.visitor_id,
    )

    await message_routine.process(conversation, message)

    if not message.text or len(message.text) == 0:
        raise HTTPException(status_code=400, detail={
            "error": f"no message content"
        })

    agent = await agent_service.get_by_id(conversation.agent_id)
    if not agent:
        raise HTTPException(status_code=400, detail={
            "error": f"agent {conversation.agent_id} not found"
        })
    message.to = ChatUser(
        id=str(agent.id),
        name=agent.name,   
    )

    print("send_message: ", message)

    memory_type: str = "conversation_buffer_window" # from agent config
    memory_options = None
    if agent.options is not None:
        memory_options = agent.options.get('memory')
        if memory_options is not None:
            memory_options = memory_options.copy()
            memory_type = memory_options.pop('type', memory_type)

    memory = await request.app.state.memory_manager.build(memory_type, message.conversation_id, memory_options or {})


    if message.metadata is not None:
        agent_type = message.metadata.get("type")

    if agent_type is None:
        if agent is not None and agent.options is not None:
            chain = agent.options.get('chain')
            if chain is not None:
                agent_type = chain.get("type")

    agent_type = agent_type or "chat"



    agent_runner = await AgentBuilder.build_agent(
        agent_type=agent_type,
        agent=agent,
        conversation=conversation,
        llm_manager=request.app.state.llm_manager,
        memory=memory,
        credentials_service=credentials_service,
        prompt_service=prompt_service,
        conversation_service=conversation_service,
        agent_tool_retriever=agent_tool_retriever,
        agent_tool_loader_manager=request.app.state.agent_tool_loader_manager,
        redis=redis,
    )

    if message.streaming:
        response = ChatMessage(
            id=str(uuid4()),
            conversation_id=message.conversation_id,
        )

        """
        # 同步方案
        generator = ChatGenerator()
        return StreamingResponse(
          streaming_response(response.dict(exclude_unset=True, exclude_none=True), generator.generator(agent_runner, message)),
          media_type="text/event-stream",
        )
        """

        async def generate(send: Send):
            return await agent_runner.run(conversation, message, stream_handler=AsyncSSEChatResponseCallbackHandler(send=send, conversation=conversation))

        # 异步方案
        return StreamingResponse(
            generate=generate,
            media_type="text/event-stream",
        )
    else:
        try:
            response = await agent_runner.run(conversation, message)      
        except Exception as e:
            print(traceback.format_exc())
            response = ChatMessage(
                conversation_id=message.conversation_id,
                text=str(e),
            )

    return MessageResponse(
        data=response,
    )