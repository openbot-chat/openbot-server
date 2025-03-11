from uuid import UUID
from typing import Optional, Dict
from datetime import datetime
from schemas.base import BaseSchema

class AIPluginSchemaBase(BaseSchema):
  schema_version: str
  contact_email: Optional[str]
  logo_url: Optional[str]
  manifest_url: str
  name_for_model: str
  name_for_human: str
  description_for_model: str
  description_for_human: Optional[str]
  auth: Optional[Dict]
  api: Optional[Dict]

class CreateAIPluginSchema(AIPluginSchemaBase):
  ...

class UpdateAIPluginSchema(BaseSchema):
  contact_email: Optional[str]
  logo_url: Optional[str]
  manifest_url: Optional[str]
  name_for_model: Optional[str]
  name_for_human: Optional[str]
  description_for_model: Optional[str]
  description_for_human: Optional[str]
  auth: Optional[Dict]
  api: Optional[Dict]

class AIPluginSchema(AIPluginSchemaBase):
  """AIPlugin"""
  id: UUID
  created_at: datetime
  updated_at: datetime