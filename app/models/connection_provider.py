from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import BaseModel



class ConnectionProviderSchemaBase(BaseSchema):
    identifier: str
    name: str
    icon: Optional[str]
    type: Optional[str]
    doc_url: Optional[str]
    options: Optional[Dict[str, Any]]
    app_id: Optional[UUID]

class CreateConnectionProviderSchema(ConnectionProviderSchemaBase):
    id: Optional[UUID]
 
class UpdateConnectionProviderSchema(BaseSchema):
    name: Optional[str]
    icon: Optional[str]
    doc_url: Optional[str]
    options: Optional[Dict[str, Any]]

class ConnectionProviderSchema(ConnectionProviderSchemaBase):
    """ConnectionProvider"""
    id: UUID
    created_at: datetime
    updated_at: datetime



from fastapi import Query

class ConnectionFilter(BaseModel):
    app_id: Optional[UUID] = Query(None)