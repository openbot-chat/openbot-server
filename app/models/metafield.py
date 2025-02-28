from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import BaseModel
from fastapi import Query


class MetafieldSchemaBase(BaseSchema):
    owner: str
    namespace: str
    owner_type: str
    owner_id: str
    key: str
    type: str
    value: str
    description: str

class CreateMetafieldSchema(BaseSchema):
    owner_type: str
    owner_id: str
    namespace: str
    key: str
    value: str
    type: str

class SetMetafieldSchema(CreateMetafieldSchema):
    ...

class UpdateMetafieldSchema(BaseSchema):
    value: Optional[str] = None
    type: Optional[str] = None

class MetafieldSchema(MetafieldSchemaBase):
    """Metafield"""
    id: UUID
    created_at: datetime
    updated_at: datetime


class MetafieldFilter(BaseModel):
    namespace: Optional[str] = Query(None)
    key: Optional[str] = Query(None)
    owner_type: Optional[str] = Query(None)
    owner_id: Optional[str] = Query(None)