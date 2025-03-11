from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import BaseModel, Field
from fastapi import Query


class ConversationSchemaBase(BaseSchema):
    provider: str
    agent_id: UUID
    user_id: Optional[str] = None
    visitor_id: Optional[str] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class CreateConversationSchema(ConversationSchemaBase):
    id: Optional[UUID]

class UpdateConversationSchema(BaseSchema):
    name: Optional[str] = None
    provider: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class ConversationSchema(ConversationSchemaBase):
    """Conversation"""
    id: UUID
    created_at: datetime
    updated_at: datetime


class ConversationFilter(BaseModel):
    user_id: Optional[UUID] = Query(None)
    provider: Optional[str] = Query(None)
    agent_id: UUID = Query(...)