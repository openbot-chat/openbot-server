from uuid import UUID
from typing import Optional, List
from fastapi import Depends, HTTPException
from repositories.sqlalchemy.conversation_repository import ConversationRepository
from repositories.sqlalchemy.message_repository import MessageRepository
from repositories.sqlalchemy.agent_repository import AgentRepository
from api.dependencies.repository import make_repository
from api.dependencies.redis import get_redis
from models.conversation import *
from models.message import *
from schemas.pagination import CursorParams, CursorPage
import os
from redis.asyncio import Redis
import json
import openai
import logging



class ConversationService:
    def __init__(
        self, 
        repository: ConversationRepository = Depends(make_repository(ConversationRepository)),
        message_repository: MessageRepository = Depends(make_repository(MessageRepository)),
        agent_repository: AgentRepository = Depends(make_repository(AgentRepository)),
    ):
        self.repository = repository
        self.message_repository = message_repository
        self.agent_repository = agent_repository

    async def create(self, in_schema: CreateConversationSchema) -> ConversationSchema:
        conversation = await self.repository.create(in_schema)
        await self._conversation_created(conversation)

        return conversation

    async def renew(self, in_schema: CreateConversationSchema) -> ConversationSchema:
        agent = await self.agent_repository.get_by_id(in_schema.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail={
                "error": f"could not create conversation, because agent {in_schema.agent_id} not found"
            })

        conversation = None
        if in_schema.id is not None:
            conversation = await self.repository.get_by_id(in_schema.id)
            if conversation is not None:
                if conversation.provider == in_schema.provider and conversation.agent_id == in_schema.agent_id and conversation.user_id == in_schema.user_id and conversation.visitor_id == in_schema.visitor_id:
                    if in_schema.options is not None and len(in_schema.options) > 0:
                        conversation = await self.update_by_id(in_schema.id, UpdateConversationSchema(options=in_schema.options))
                    return conversation

        in_schema.id = None

        new_conversation = await self.create(in_schema)
        
        return new_conversation

    async def clear(self, id: str):
        await self.message_repository.delete_by_conversation_id(id)

    # TODO 缓存
    async def get_by_id(self, id: UUID) -> Optional[ConversationSchema]:
        return await self.repository.get_by_id(id)

    async def update_by_id(self, id: UUID, data: UpdateConversationSchema) -> ConversationSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> None:
        await self.repository.delete_by_id(id)
        return

    async def paginate(self, filter: ConversationFilter, params: Optional[CursorParams] = None) -> CursorPage[ConversationSchema]:
        page = await self.repository.paginate1(filter, params=params)
        page.total = await self.repository.count1(filter);
        return page

    async def count(self, filter: ConversationFilter) -> int:
        return await self.repository.count1(filter)


    async def list_messages(self, conversation_id: str, params: Optional[CursorParams] = None) -> CursorPage[MessageSchema]:
        conversation = await self.repository.get_by_id(UUID(hex=conversation_id))
        if not conversation:
            raise HTTPException(status_code=404, detail={
                "error": f"could not found conversation {conversation_id}"
            })

        return await self.message_repository.list_messages(MessageFilter(
            conversation_id=conversation_id,
        ), params)
        


    async def add_message(self, message: CreateMessageSchema) -> MessageSchema:
        conversation = await self.repository.get_by_id(UUID(hex=message.conversation_id))
        if not conversation:
            raise HTTPException(status_code=404, detail={
                "error": f"could not found conversation {message.conversation_id}"
            })

        return await self.message_repository.create(message)
        


    async def _conversation_created(self, conversation: ConversationSchema):
        agent = await self.agent_repository.get_by_id(conversation.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail={
                "error": f"could not create conversation, because agent {conversation.agent_id} not found"
            })
        
        new_options = (conversation.options or {}).copy()

        # openai assistant
        agent_options = agent.options or {}
        provider = agent_options.get('provider')
        if provider == 'openai_assistant':
            provider_options = agent_options.get(provider, {})
            api_key = provider_options.get('api_key')
            organization = provider_options.get('organization')

            client = openai.AsyncOpenAI(api_key=api_key, organization=organization)
            thread = await client.beta.threads.create()
            new_options['thread_id'] = thread.id
            print(f'openai assistant thread {thread.id} created')

            await self.repository.update_by_id(conversation.id, UpdateConversationSchema(options=new_options))