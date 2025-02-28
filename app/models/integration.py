from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema
from pydantic import Field

class IntegrationSchemaBase(BaseSchema): 
    name: str
    identifier: str
    catalog: str
    icon: Optional[str]
    options: Dict[str, Any] = Field(default_factory=dict, alias="options")
    is_public: Optional[bool]
    description: Optional[str]

class CreateIntegrationSchema(BaseSchema):
    identifier: str
    catalog: str
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateIntegrationSchema(BaseSchema):
    name: Optional[str]
    icon: Optional[str]
    description: Optional[str]
    is_public: Optional[bool]
    options: Optional[Dict[str, Any]]

class IntegrationSchema(IntegrationSchemaBase):
    """Integration"""
    id: UUID
    created_at: datetime
    updated_at: datetime