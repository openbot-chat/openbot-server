from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from schemas.base import BaseSchema
from .tool import *



class ToolkitSchemaBase(BaseSchema):
    name: str
    description: str
    icon: Optional[str] = None
    type: str
    options: Optional[Dict[str, Any]]
    org_id: Optional[str]
    tools: List[ToolSchema]

class CreateToolkitSchema(BaseSchema):
    name: str
    description: str
    icon: Optional[str] = None
    type: str
    options: Optional[Dict[str, Any]]
    org_id: Optional[str]

class UpdateToolkitSchema(BaseSchema):
    name: Optional[str]
    description: Optional[str]
    icon: Optional[str] = None
    options: Optional[Dict[str, Any]]

class ToolkitSchema(ToolkitSchemaBase):
    """Toolkit"""
    id: UUID
    created_at: datetime
    updated_at: datetime