from uuid import UUID
from typing import Optional, List
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import Field

class PromptSchemaBase(BaseSchema):
    name: str
    content: str
    input_variables: Optional[List[str]] = Field(default=[])
    org_id: str

class CreatePromptSchema(PromptSchemaBase):
    ...

class UpdatePromptSchema(BaseSchema):
    name: Optional[str]
    content: Optional[str]
    input_variables: Optional[List[str]]

class PromptSchema(PromptSchemaBase):
    """Prompt"""
    id: UUID
    created_at: datetime
    updated_at: datetime