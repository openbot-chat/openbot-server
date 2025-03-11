from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema
from .connection_provider import ConnectionProviderSchema



class ActionConnectionProviderSchemaBase(BaseSchema):
    action_id: UUID
    connection_provider_id: UUID
    connection_provider: Optional[ConnectionProviderSchema]

class CreateActionConnectionProviderSchema(BaseSchema):
    action_id: UUID
    connection_provider_id: UUID

class ActionConnectionProviderSchema(ActionConnectionProviderSchemaBase):
    """ActionConnectionProvider"""
    id: UUID
    created_at: datetime
    updated_at: datetime