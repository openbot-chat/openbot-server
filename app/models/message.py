from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import BaseModel
from fastapi import Query


class MessageSchemaBase(BaseSchema):
    agent_id: str
    conversation_id: str
    type: str
    text: str

class CreateMessageSchema(MessageSchemaBase):
    ...

class UpdateMessageSchema(BaseSchema):
    type: Optional[str] = None
    text: Optional[str] = None

class MessageSchema(MessageSchemaBase):
    """Message"""
    id: UUID
    created_at: datetime
    updated_at: datetime


class MessageFilter(BaseModel):
    conversation_id: Optional[str] = Query(None)
    agent_id: Optional[str] = Query(None)