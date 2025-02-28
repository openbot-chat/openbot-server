from uuid import UUID
from typing import Optional, Dict, List, Any
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import BaseModel



class VoiceSchemaBase(BaseSchema):
    provider: str
    name: str
    language: Optional[str]
    gender: Optional[str]
    identifier: str
    options: Optional[Dict[str, Any]]
    creator_id: Optional[str]
    styles: Optional[List[str]]
    private: bool = False
    type: Optional[str]
    is_cloned: bool = False
    sample: Optional[str]

class CreateVoiceSchema(VoiceSchemaBase):
    ...

class UpdateVoiceSchema(BaseSchema):
    provider: str
    name: str
    language: str
    gender: str
    identifier: str
    private: bool
    options: Optional[Dict[str, Any]]

class VoiceSchema(VoiceSchemaBase):
    id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class SayRequest(BaseModel):
    provider: str
    format: Optional[str] = 'base64'
    identifier: str
    style: Optional[str] = ''
    pitch: int = 1
    rate: int = 1
    volume: int = 1
    text: str
    options: Optional[Dict[str, Any]] = None

class SayResponse(BaseModel):
    duration: Optional[float] = None
    format: str = 'base64'
    data: Optional[str] = None
    url: Optional[str] = None

class TranscribeResponse(BaseModel):
    text: str