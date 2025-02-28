from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema



class DatasourceSchemaBase(BaseSchema):
    name: str
    type: str
    status: str
    last_sync: Optional[datetime]
    options: Optional[Dict[str, Any]] = {}
    metadata_: Optional[Dict[str, Any]] = {}
    documents: Optional[int] = 0
    datastore_id: UUID
    org_id: str

class CreateDatasourceSchema(BaseSchema):
    name: str
    type: str
    options: Optional[Dict[str, Any]] = None
    metadata_: Optional[Dict[str, Any]] = None
    datastore_id: Optional[UUID] = None
    org_id: str

class UpdateDatasourceSchema(BaseSchema):
    name: Optional[str] = None
    status: Optional[str] = None
    last_sync: Optional[datetime] = None
    options: Optional[Dict[str, Any]] = None
    metadata_: Optional[Dict[str, Any]] = None

class DatasourceSchema(DatasourceSchemaBase):
    """Datasource"""
    id: UUID
    created_at: datetime
    updated_at: datetime