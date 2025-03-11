from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from schemas.base import BaseSchema


class CategorySchemaBase(BaseSchema):
    name: str
    description: str
    icon: Optional[str] = None
    type: str
    options: Optional[Dict[str, Any]]

class CreateCategorySchema(CategorySchemaBase):
    ...

class UpdateCategorySchema(BaseSchema):
    name: Optional[str]
    description: Optional[str]
    icon: Optional[str] = None
    options: Optional[Dict[str, Any]]

class CategorySchema(CategorySchemaBase):
    """Category"""
    id: UUID
    created_at: datetime
    updated_at: datetime