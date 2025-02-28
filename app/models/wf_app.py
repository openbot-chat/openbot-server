from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import BaseModel
from .wf_action import *
from .connection_provider import *



class AppSchemaBase(BaseSchema):
    name: str
    description: str
    icon: Optional[str] = None
    theme: Optional[str] = None
    options: Optional[Dict[str, Any]]
    actions: List[ActionSchema]
    connections: List[ConnectionProviderSchema]
    org_id: Optional[str] = None

class CreateAppSchema(BaseSchema):
    name: str
    description: str
    icon: Optional[str] = None
    theme: Optional[str] = None
    options: Optional[Dict[str, Any]]
    org_id: Optional[str] = None

class UpdateAppSchema(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    theme: Optional[str] = None
    options: Optional[Dict[str, Any]]

class AppSchema(AppSchemaBase):
    """App"""
    id: UUID
    created_at: datetime
    updated_at: datetime


from fastapi import Query

class AppFilter(BaseModel):
    org_id: Optional[str] = Query(None)
    name: Optional[str] = Query(None)