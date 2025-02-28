from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import Field



class CredentialsSchemaBase(BaseSchema):
    name: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    org_id: Optional[str] = None

class CreateCredentialsSchema(BaseSchema):
    name: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    org_id: str

class UpdateCredentialsSchema(BaseSchema):
    name: Optional[str]
    data: Optional[Dict[str, Any]]

class CredentialsSchema(CredentialsSchemaBase):
    """Prompt Template"""
    id: UUID
    created_at: datetime
    updated_at: datetime