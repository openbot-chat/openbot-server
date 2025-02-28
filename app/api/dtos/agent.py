from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from models.agent import AvatarConfigSchema, VoiceConfigSchema, Visibility
from uuid import UUID
from fastapi import Query


class PublicAgentDTO(BaseModel):
    id: UUID
    name: str
    avatar: Optional[AvatarConfigSchema]
    voice: Optional[VoiceConfigSchema]
    cognition: Optional[Dict[str, Any]] = None    
    identifier: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str]


class AgentFilter(BaseModel):
    org_id: Optional[str] = Query(None)
    visibility: Optional[Visibility] = Query(None)

class CreateAgentToolDTO(BaseModel):
    tool_id: UUID
    options: Dict[str, Any] = Field(default_factory=dict)
    name: Optional[str] = None
    description: Optional[str] = None
    return_direct: Optional[bool] = False

class AgentSayRequest(BaseModel):
    format: Optional[str] = 'base64'
    pitch: int = 1
    rate: int = 1
    volume: int = 1
    style: str = ''
    text: str
    options: Optional[Dict[str, Any]] = None