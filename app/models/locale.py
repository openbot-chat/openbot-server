from uuid import UUID
from datetime import datetime
from schemas.base import BaseSchema

class LocaleSchemaBase(BaseSchema):
    label: str
    locale: str

class LocaleSchema(LocaleSchemaBase):
    """Locale"""
    id: UUID
    created_at: datetime
    updated_at: datetime