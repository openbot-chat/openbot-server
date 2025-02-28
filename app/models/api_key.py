from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema

class ApiKeySchemaBase(BaseSchema):
    name: str
    token: str
    expires_in: int = 86400 * 365
    user_id: str


class CreateApiKeySchema(BaseSchema):
    name: str
    token: Optional[str] = None
    expires_in: Optional[int] = 86400 * 365
    user_id: Optional[str] = None

class UpdateApiKeySchema(BaseSchema):
    name: Optional[str] = None
    token: Optional[str] = None
    expires_in: Optional[int] = 86400 * 365

class ApiKeySchema(ApiKeySchemaBase):
    """Api Key"""
    id: UUID
    created_at: datetime
    updated_at: datetime