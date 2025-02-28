from uuid import UUID
from typing import Optional, Dict, List, Any, Type
from pydantic import Field
from datetime import datetime
from schemas.base import BaseSchema
from .agent_datastore import AgentDatastoreSchema
from .agent_tool import AgentToolSchema
from .avatar import AvatarSchemaBase
from .voice import VoiceSchemaBase
from enum import Enum



class Visibility(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'

class AvatarConfigSchema(AvatarSchemaBase):
    id: Optional[str]

class VoiceConfigSchema(VoiceSchemaBase):
    id: Optional[str] = None
    pitch: int = 1
    rate: int = 1
    volume: int = 1
    style: Optional[str] = None

class AgentSchemaBase(BaseSchema):
    name: str
    avatar: Optional[AvatarConfigSchema]
    voice: Optional[VoiceConfigSchema]
    cognition: Optional[Dict[str, Any]] = None    
    identifier: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    visibility: Optional[Visibility] = Visibility.PUBLIC
    creator_id: Optional[str] = None
    org_id: Optional[str]
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    datastores: Optional[List[AgentDatastoreSchema]] = None
    tools: Optional[List[AgentToolSchema]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata_")


class CreateAgentSchema(BaseSchema):
    name: str
    avatar: Optional[AvatarConfigSchema]
    voice: Optional[VoiceConfigSchema]
    cognition: Optional[Dict[str, Any]] = None    
    identifier: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    visibility: Optional[str] = "public"
    creator_id: Optional[str] = None
    org_id: str
    options: Optional[Dict[str, Any]] = None
    template_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata_")

class UpdateAgentSchema(BaseSchema):
    name: Optional[str] = None
    avatar: Optional[AvatarConfigSchema] = None
    voice: Optional[VoiceConfigSchema] = None
    cognition: Optional[Dict[str, Any]] = None
    identifier: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    options: Optional[Dict[str, Any]]
    visibility: Optional[str] = "public"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata_")

class AgentSchema(AgentSchemaBase):
    """Agent"""
    id: UUID
    created_at: datetime
    updated_at: datetime