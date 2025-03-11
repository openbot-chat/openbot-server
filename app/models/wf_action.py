from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from schemas.base import BaseSchema
from .action_connection_provider import *


class ActionSchemaBase(BaseSchema):
    identifier: str
    name: str
    description: str
    options: Optional[Dict[str, Any]]
    app_id: UUID
    options: Optional[Dict[str, Any]]

class CreateActionSchema(ActionSchemaBase):
    ...

class UpdateActionSchema(BaseSchema):
    identifier: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    options: Optional[Dict[str, Any]]

class ActionSchema(ActionSchemaBase):
    """Action"""
    id: UUID
    connection_providers: List[ActionConnectionProviderSchema]
    created_at: datetime
    updated_at: datetime