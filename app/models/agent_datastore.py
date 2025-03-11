from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema
from .datastore import DatastoreSchema



class AgentDatastoreSchemaBase(BaseSchema):
    agent_id: UUID
    datastore_id: UUID
    datastore: Optional[DatastoreSchema]
    options: Optional[Dict[str, Any]]

class CreateAgentDatastoreSchema(BaseSchema):
    agent_id: UUID
    datastore_id: UUID

class UpdateAgentDatastoreSchema(BaseSchema):
    options: Optional[Dict[str, Any]]

class AgentDatastoreSchema(AgentDatastoreSchemaBase):
    """AgentDatastore"""
    id: UUID
    created_at: datetime
    updated_at: datetime