from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema

class DatastoreSchemaBase(BaseSchema):
    name_for_model: str
    description_for_model: str
    provider: str = "qdrant"
    options: Optional[Dict[str, Any]]
    collection_name: str
    org_id: Optional[str]
    agent_count: Optional[int]
    datasource_count: Optional[int]
    # visibility: str

class CreateDatastoreSchema(BaseSchema):
    id: Optional[UUID]
    name_for_model: str
    description_for_model: str
    provider: str = "qdrant"
    options: Optional[Dict[str, Any]]
    collection_name: Optional[str]
    org_id: Optional[str]


class UpdateDatastoreSchema(BaseSchema):
    name_for_model: Optional[str]
    description_for_model: Optional[str]

class DatastoreSchema(DatastoreSchemaBase):
    """Prompt Template"""
    id: UUID
    created_at: datetime
    updated_at: datetime