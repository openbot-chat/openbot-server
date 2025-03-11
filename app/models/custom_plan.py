from uuid import UUID
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema


class CustomPlanSchemaBase(BaseSchema):
    external_id: str
    name: str
    org_id: str
    claimed_at: datetime
    description: Optional[str]
    price: int
    currency: str
    is_yearly: Optional[bool] = False
    storage_limit: int = 0
    token_limit: int = 0
    chats_limit: int = 0
    # is_quarantined: bool

class CreateCustomPlanSchema(CustomPlanSchemaBase):
    ...

class UpdateCustomPlanSchema(BaseSchema):
    name: Optional[str]
    claimed_at: datetime
    description: Optional[str]
    price: Optional[int]
    currency: Optional[str]
    is_yearly: Optional[bool] = False
    storage_limit: Optional[int]
    token_limit: Optional[int]
    chats_limit: Optional[int]

class CustomPlanSchema(CustomPlanSchemaBase):
    """CustomPlan"""
    id: UUID
    created_at: datetime
    updated_at: datetime