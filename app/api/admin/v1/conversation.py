
from typing import List, Union, Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from models.message import MessageSchema
from models.message import CreateMessageSchema, MessageSchema
from models.conversation import *
from schemas.pagination import CursorParams, CursorPage
from services import (
    ConversationService,
    AgentService,
)

from api.dtos.conversation import *


router = APIRouter()

@router.get(
    '/{conversation_id}/messages',
    response_model=CursorPage[MessageSchema],
    response_model_exclude_unset=True,
)
async def list_messages(
    conversation_id: str,
    params: CursorParams = Depends(),
    conversation_service: ConversationService = Depends(ConversationService)
):
    return await conversation_service.list_messages(conversation_id, params)

@router.post('', response_model=ConversationSchema)
async def create_conversation(
    request: Request,
    data: CreateConversationSchema,    
    conversation_service: ConversationService = Depends(ConversationService),
):
    return await conversation_service.create(data)

@router.get('/{conversation_id}', response_model=ConversationSchema)
async def get_by_id(
    conversation_id: UUID,    
    conversation_service: ConversationService = Depends(ConversationService),
):
    return await conversation_service.get_by_id(conversation_id)


@router.patch('/{conversation_id}', response_model=ConversationSchema)
async def update_conversation(
    request: Request,
    conversation_id: UUID,
    data: UpdateConversationSchema,
    conversation_service: ConversationService = Depends(ConversationService),
):
    return await conversation_service.update_by_id(conversation_id, data)

@router.post('/{conversation_id}/clear')
async def clear_conversation(
    request: Request,
    conversation_id: str,
    conversation_service: ConversationService = Depends(ConversationService),
):
    return await conversation_service.clear(conversation_id)


@router.post('/renew', response_model=ConversationSchema)
async def renew_conversation(
    request: Request,
    data: CreateConversationSchema,    
    conversation_service: ConversationService = Depends(ConversationService),
):
    return await conversation_service.renew(data)


@router.delete(
    '/{conversation_id}'
)
async def delete_conversation(
    request: Request,
    conversation_id: UUID,
    conversation_service: ConversationService = Depends(ConversationService),
):
    return await conversation_service.delete_by_id(conversation_id)

@router.post(
    '/{conversation_id}/messages',
    response_model=MessageSchema,
)
async def add_message(
    request: Request,
    conversation_id: UUID,
    data: CreateMessageDTO,
    conversation_service: ConversationService = Depends(ConversationService),
):
    conversation = await conversation_service.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail={
            "error": f"could not found conversation {conversation_id}"
        })

    message = CreateMessageSchema(
        text=data.text,
        type=data.type,
        conversation_id=str(conversation_id),
        agent_id=str(conversation.agent_id),
    )
    return await conversation_service.add_message(message)


@router.get("", response_model=CursorPage[ConversationSchema], response_model_exclude_unset=True)
async def list_conversations(
    filter: ConversationFilter = Depends(None),
    params: CursorParams = Depends(None),
    conversation_service: ConversationService = Depends(ConversationService),
    agent_service: AgentService = Depends(AgentService),
):
    """conversations list"""
    agent = await agent_service.get_by_id(filter.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail={"error": "agent not found"})

    return await conversation_service.paginate(filter, params)
