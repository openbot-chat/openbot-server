from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import Field

class DocumentSchemaBase(BaseSchema): 
    last_sync: Optional[datetime]
    metadata_: Optional[Dict[str, Any]] = Field(default_factory=dict)
    text: Optional[str]
    datasource_id: UUID
    org_id: str

class CreateDocumentSchema(BaseSchema):
    id: Optional[UUID]
    metadata_: Optional[Dict[str, Any]]
    datasource_id: UUID
    org_id: str

class UpdateDocumentSchema(BaseSchema):
    last_sync: Optional[datetime]
    metadata_: Optional[Dict[str, Any]]
    text: Optional[str]

class DocumentSchema(DocumentSchemaBase):
    """Document"""
    id: UUID
    created_at: datetime
    updated_at: datetime