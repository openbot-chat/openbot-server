
from typing import List, Union, Any, Dict

from fastapi import APIRouter, Depends, Request, HTTPException
from models.conversation import *
from models.message import *
from schemas.pagination import CursorParams, CursorPage
from services import (
    ConversationService,
    AgentService,
)
from api.dependencies.auth import get_auth_user
from api.dtos.conversation import *
from security.auth0.auth import Auth0User
from models.message import *
from uuid import UUID


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
    user: Auth0User = Depends(get_auth_user),
):
    return await conversation_service.create(data)

@router.post('/renew', response_model=ConversationSchema)
async def renew_conversation(
    request: Request,
    data: CreateConversationSchema,    
    conversation_service: ConversationService = Depends(ConversationService),
    user: Auth0User = Depends(get_auth_user),
):
    return await conversation_service.renew(data)


@router.delete(
    '/{conversation_id}'
)
async def delete_conversation(
    request: Request,
    conversation_id: UUID,
    conversation_service: ConversationService = Depends(ConversationService),
    user: Auth0User = Depends(get_auth_user),    
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
    user: Auth0User = Depends(get_auth_user),
):
    """conversations list"""
    agent = await agent_service.get_by_id(filter.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail={"error": "agent not found"})

    return await conversation_service.paginate(filter, params)
