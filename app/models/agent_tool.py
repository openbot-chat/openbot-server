from uuid import UUID
from typing import Dict, Any, Optional
from datetime import datetime
from schemas.base import BaseSchema
from .tool import ToolSchema
from pydantic import Field, BaseModel


class AgentToolSchemaBase(BaseSchema):
    agent_id: UUID
    tool_id: UUID
    tool: Optional[ToolSchema] = None
    return_direct: bool = False
    options: Dict[str, Any] = Field(default_factory=dict)
    name: Optional[str] = None
    description: Optional[str] = None
    
class CreateAgentToolSchema(BaseSchema):
    agent_id: UUID
    tool_id: UUID
    options: Dict[str, Any] = Field(default_factory=dict)
    name: Optional[str] = None
    description: Optional[str] = None
    return_direct: Optional[bool] = False

class UpdateAgentToolSchema(BaseSchema):
    options: Optional[Dict[str, Any]] = None
    name: Optional[str]
    description: Optional[str]
    return_direct: Optional[bool] = False

class AgentToolSchema(AgentToolSchemaBase):
    """AgentTool"""
    id: UUID
    created_at: datetime
    updated_at: datetime

class AgentToolFilter(BaseModel):
    agent_id: Optional[UUID] = None